"""Issues management API endpoints for Elder enterprise features."""

from flask import Blueprint, jsonify, request, g
from marshmallow import ValidationError
from datetime import datetime, timezone

from apps.api.auth.decorators import login_required, resource_role_required
from apps.api.models.issue import (
    Issue,
    IssueLabel,
    IssueComment,
    IssueEntityLink,
    IssueStatus,
    IssuePriority,
    IssueLinkType,
    get_organization_issues_recursive,
    get_entity_issues,
)
from apps.api.models.resource_role import ResourceRole, ResourceType, ResourceRoleType
from apps.api.schemas.issue import (
    IssueSchema,
    IssueCreateSchema,
    IssueUpdateSchema,
    IssueFilterSchema,
    IssueListSchema,
    IssueCommentSchema,
    IssueCommentCreateSchema,
    IssueLabelSchema,
    IssueLabelCreateSchema,
    IssueEntityLinkSchema,
    IssueEntityLinkCreateSchema,
)
from shared.api_utils import get_or_404, make_error_response, paginate
from shared.database import db
from shared.licensing import license_required

bp = Blueprint("issues", __name__)


@bp.route("", methods=["GET"])
@login_required
@license_required("enterprise")
def list_issues():
    """
    List issues with optional filtering.

    Query Parameters:
        - resource_type: Filter by resource type (entity/organization)
        - resource_id: Filter by resource ID
        - status: Filter by status (open/in_progress/closed/resolved)
        - priority: Filter by priority (low/medium/high/critical)
        - assigned_to_id: Filter by assignee
        - created_by_id: Filter by creator
        - label_id: Filter by label
        - page: Page number (default: 1)
        - per_page: Items per page (default: 50)

    Returns:
        200: List of issues with pagination
        400: Invalid parameters
        403: License required

    Example:
        GET /api/v1/issues?resource_type=entity&resource_id=42&status=open
    """
    # Validate query parameters
    filter_schema = IssueFilterSchema()
    try:
        filters = filter_schema.load(request.args)
    except ValidationError as e:
        return make_error_response(str(e.messages), 400)

    # Build query
    query = db.session.query(Issue)

    # Apply filters
    if "resource_type" in filters:
        query = query.filter_by(resource_type=filters["resource_type"])
    if "resource_id" in filters:
        query = query.filter_by(resource_id=filters["resource_id"])
    if "status" in filters:
        query = query.filter_by(status=IssueStatus(filters["status"]))
    if "priority" in filters:
        query = query.filter_by(priority=IssuePriority(filters["priority"]))
    if "assigned_to_id" in filters:
        query = query.filter_by(assigned_to_id=filters["assigned_to_id"])
    if "created_by_id" in filters:
        query = query.filter_by(created_by_id=filters["created_by_id"])
    if "label_id" in filters:
        # Filter by label (join through association table)
        from apps.api.models.issue import issue_label_assignments
        query = query.join(issue_label_assignments).filter(
            issue_label_assignments.c.label_id == filters["label_id"]
        )

    # Order by creation date (newest first)
    query = query.order_by(Issue.created_at.desc())

    # Paginate
    items, pagination = paginate(query, filters["page"], filters["per_page"])

    # Serialize response
    list_schema = IssueListSchema()
    return jsonify(list_schema.dump({"items": items, **pagination})), 200


@bp.route("", methods=["POST"])
@login_required
@license_required("enterprise")
@resource_role_required("viewer")
def create_issue():
    """
    Create a new issue.

    Requires viewer role on the resource.

    Request Body:
        {
            "resource_type": "entity",
            "resource_id": 42,
            "title": "Server not responding",
            "description": "The web server is returning 500 errors",
            "priority": "high",
            "assigned_to_id": 5,
            "due_date": "2024-12-31T23:59:59Z",
            "label_ids": [1, 2]
        }

    Returns:
        201: Issue created
        400: Invalid request
        403: License required or insufficient permissions

    Example:
        POST /api/v1/issues
    """
    # Validate request
    create_schema = IssueCreateSchema()
    try:
        data = create_schema.load(request.get_json())
    except ValidationError as e:
        return make_error_response(str(e.messages), 400)

    # Create issue
    issue = Issue(
        resource_type=data["resource_type"],
        resource_id=data["resource_id"],
        title=data["title"],
        description=data.get("description"),
        priority=IssuePriority(data["priority"]),
        status=IssueStatus.OPEN,
        created_by_id=g.current_user.id,
        assigned_to_id=data.get("assigned_to_id"),
        due_date=data.get("due_date"),
    )

    db.session.add(issue)
    db.session.flush()  # Get issue ID

    # Add labels if provided
    if data.get("label_ids"):
        labels = db.session.query(IssueLabel).filter(IssueLabel.id.in_(data["label_ids"])).all()
        issue.labels.extend(labels)

    db.session.commit()

    # Serialize response
    schema = IssueSchema()
    return jsonify(schema.dump(issue)), 201


@bp.route("/<int:id>", methods=["GET"])
@login_required
@license_required("enterprise")
def get_issue(id: int):
    """
    Get a single issue by ID.

    Path Parameters:
        - id: Issue ID

    Returns:
        200: Issue details
        403: License required
        404: Issue not found

    Example:
        GET /api/v1/issues/1
    """
    issue = get_or_404(Issue, id)

    # Serialize response
    schema = IssueSchema()
    return jsonify(schema.dump(issue)), 200


@bp.route("/<int:id>", methods=["PATCH"])
@login_required
@license_required("enterprise")
def update_issue(id: int):
    """
    Update an issue.

    Requires maintainer role to edit fields.
    Requires operator role to close issue.

    Path Parameters:
        - id: Issue ID

    Request Body:
        {
            "title": "Updated title",
            "description": "Updated description",
            "status": "closed",
            "priority": "critical",
            "assigned_to_id": 10,
            "due_date": "2024-12-31T23:59:59Z"
        }

    Returns:
        200: Issue updated
        400: Invalid request
        403: License required or insufficient permissions
        404: Issue not found

    Example:
        PATCH /api/v1/issues/1
    """
    issue = get_or_404(Issue, id)

    # Validate request
    update_schema = IssueUpdateSchema()
    try:
        data = update_schema.load(request.get_json())
    except ValidationError as e:
        return make_error_response(str(e.messages), 400)

    # Check permissions based on what's being updated
    is_closing = "status" in data and data["status"] in ["closed", "resolved"]
    is_editing = any(k in data for k in ["title", "description", "priority", "assigned_to_id", "due_date"])

    # Determine resource type and ID from issue
    resource_type = ResourceType.ENTITY if issue.resource_type == "entity" else ResourceType.ORGANIZATION

    # Closing requires operator role
    if is_closing:
        has_permission = ResourceRole.check_permission(
            identity_id=g.current_user.id,
            resource_type=resource_type,
            resource_id=issue.resource_id,
            required_role=ResourceRoleType.OPERATOR,
        )

        if not has_permission and not g.current_user.is_superuser:
            return (
                jsonify(
                    {
                        "error": "Insufficient permissions",
                        "message": "Closing issues requires operator role",
                    }
                ),
                403,
            )

    # Editing requires maintainer role
    if is_editing:
        has_permission = ResourceRole.check_permission(
            identity_id=g.current_user.id,
            resource_type=resource_type,
            resource_id=issue.resource_id,
            required_role=ResourceRoleType.MAINTAINER,
        )

        if not has_permission and not g.current_user.is_superuser:
            return (
                jsonify(
                    {
                        "error": "Insufficient permissions",
                        "message": "Editing issues requires maintainer role",
                    }
                ),
                403,
            )

    # Update fields
    if "title" in data:
        issue.title = data["title"]
    if "description" in data:
        issue.description = data["description"]
    if "priority" in data:
        issue.priority = IssuePriority(data["priority"])
    if "assigned_to_id" in data:
        issue.assigned_to_id = data["assigned_to_id"]
    if "due_date" in data:
        issue.due_date = data["due_date"]

    # Handle status change
    if "status" in data:
        new_status = IssueStatus(data["status"])
        if new_status in [IssueStatus.CLOSED, IssueStatus.RESOLVED]:
            issue.close(g.current_user.id)
            issue.status = new_status
        else:
            issue.reopen()
            issue.status = new_status

    db.session.commit()

    # Serialize response
    schema = IssueSchema()
    return jsonify(schema.dump(issue)), 200


@bp.route("/<int:id>", methods=["DELETE"])
@login_required
@license_required("enterprise")
def delete_issue(id: int):
    """
    Delete an issue.

    Requires maintainer role on the resource.

    Path Parameters:
        - id: Issue ID

    Returns:
        204: Issue deleted
        403: License required or insufficient permissions
        404: Issue not found

    Example:
        DELETE /api/v1/issues/1
    """
    issue = get_or_404(Issue, id)

    # Check maintainer permission
    resource_type = ResourceType.ENTITY if issue.resource_type == "entity" else ResourceType.ORGANIZATION

    if not g.current_user.is_superuser:
        has_permission = ResourceRole.check_permission(
            identity_id=g.current_user.id,
            resource_type=resource_type,
            resource_id=issue.resource_id,
            required_role=ResourceRoleType.MAINTAINER,
        )

        if not has_permission:
            return (
                jsonify(
                    {
                        "error": "Insufficient permissions",
                        "message": "Deleting issues requires maintainer role",
                    }
                ),
                403,
            )

    # Delete issue (cascade will delete comments and links)
    db.session.delete(issue)
    db.session.commit()

    return "", 204


# ============================================================================
# Issue Comments Endpoints
# ============================================================================


@bp.route("/<int:id>/comments", methods=["GET"])
@login_required
@license_required("enterprise")
def list_issue_comments(id: int):
    """
    List all comments for an issue.

    Path Parameters:
        - id: Issue ID

    Returns:
        200: List of comments (ordered by creation date)
        403: License required
        404: Issue not found

    Example:
        GET /api/v1/issues/1/comments
    """
    issue = get_or_404(Issue, id)

    # Serialize comments (already ordered by created_at in model)
    schema = IssueCommentSchema(many=True)
    return jsonify(schema.dump(issue.comments)), 200


@bp.route("/<int:id>/comments", methods=["POST"])
@login_required
@license_required("enterprise")
@resource_role_required("viewer")
def create_issue_comment(id: int):
    """
    Add a comment to an issue.

    Requires viewer role on the resource.

    Path Parameters:
        - id: Issue ID

    Request Body:
        {
            "content": "This is a comment with **Markdown** support"
        }

    Returns:
        201: Comment created
        400: Invalid request
        403: License required or insufficient permissions
        404: Issue not found

    Example:
        POST /api/v1/issues/1/comments
    """
    issue = get_or_404(Issue, id)

    # Validate request
    create_schema = IssueCommentCreateSchema()
    try:
        data = create_schema.load(request.get_json())
    except ValidationError as e:
        return make_error_response(str(e.messages), 400)

    # Create comment
    comment = IssueComment(
        issue_id=issue.id,
        author_id=g.current_user.id,
        content=data["content"],
    )

    db.session.add(comment)
    db.session.commit()

    # Serialize response
    schema = IssueCommentSchema()
    return jsonify(schema.dump(comment)), 201


@bp.route("/<int:id>/comments/<int:comment_id>", methods=["DELETE"])
@login_required
@license_required("enterprise")
def delete_issue_comment(id: int, comment_id: int):
    """
    Delete a comment from an issue.

    Requires maintainer role OR being the comment author.

    Path Parameters:
        - id: Issue ID
        - comment_id: Comment ID

    Returns:
        204: Comment deleted
        403: License required or insufficient permissions
        404: Issue or comment not found

    Example:
        DELETE /api/v1/issues/1/comments/5
    """
    issue = get_or_404(Issue, id)
    comment = get_or_404(IssueComment, comment_id)

    # Verify comment belongs to issue
    if comment.issue_id != issue.id:
        return make_error_response("Comment does not belong to this issue", 400)

    # Check permission: maintainer or comment author
    resource_type = ResourceType.ENTITY if issue.resource_type == "entity" else ResourceType.ORGANIZATION

    is_author = comment.author_id == g.current_user.id
    is_maintainer = ResourceRole.check_permission(
        identity_id=g.current_user.id,
        resource_type=resource_type,
        resource_id=issue.resource_id,
        required_role=ResourceRoleType.MAINTAINER,
    )

    if not (is_author or is_maintainer or g.current_user.is_superuser):
        return (
            jsonify(
                {
                    "error": "Insufficient permissions",
                    "message": "Only maintainers or comment authors can delete comments",
                }
            ),
            403,
        )

    # Delete comment
    db.session.delete(comment)
    db.session.commit()

    return "", 204


# ============================================================================
# Issue Labels Endpoints
# ============================================================================


@bp.route("/labels", methods=["GET"])
@login_required
def list_issue_labels():
    """
    List all available issue labels.

    Public endpoint (no license required for reading).

    Returns:
        200: List of labels

    Example:
        GET /api/v1/issues/labels
    """
    labels = db.session.query(IssueLabel).order_by(IssueLabel.name).all()

    # Serialize response
    schema = IssueLabelSchema(many=True)
    return jsonify(schema.dump(labels)), 200


@bp.route("/labels", methods=["POST"])
@login_required
@license_required("enterprise")
def create_issue_label():
    """
    Create a new issue label.

    Requires enterprise license.

    Request Body:
        {
            "name": "bug",
            "color": "#ff0000",
            "description": "Something isn't working"
        }

    Returns:
        201: Label created
        400: Invalid request
        403: License required
        409: Label already exists

    Example:
        POST /api/v1/issues/labels
    """
    # Validate request
    create_schema = IssueLabelCreateSchema()
    try:
        data = create_schema.load(request.get_json())
    except ValidationError as e:
        return make_error_response(str(e.messages), 400)

    # Check if label already exists
    existing = db.session.query(IssueLabel).filter_by(name=data["name"]).first()
    if existing:
        return (
            jsonify(
                {
                    "error": "Label already exists",
                    "message": f"Label '{data['name']}' already exists",
                    "existing_label_id": existing.id,
                }
            ),
            409,
        )

    # Create label
    label = IssueLabel(
        name=data["name"],
        color=data.get("color", "#808080"),
        description=data.get("description"),
    )

    db.session.add(label)
    db.session.commit()

    # Serialize response
    schema = IssueLabelSchema()
    return jsonify(schema.dump(label)), 201


@bp.route("/<int:id>/labels", methods=["POST"])
@login_required
@license_required("enterprise")
@resource_role_required("operator")
def add_issue_label(id: int):
    """
    Add a label to an issue.

    Requires operator role on the resource.

    Path Parameters:
        - id: Issue ID

    Request Body:
        {
            "label_id": 1
        }

    Returns:
        200: Label added
        400: Invalid request
        403: License required or insufficient permissions
        404: Issue or label not found

    Example:
        POST /api/v1/issues/1/labels
    """
    issue = get_or_404(Issue, id)

    # Get label_id from request
    data = request.get_json() or {}
    label_id = data.get("label_id")

    if not label_id:
        return make_error_response("label_id required", 400)

    label = get_or_404(IssueLabel, label_id)

    # Check if label already added
    if label in issue.labels:
        return make_error_response("Label already added to this issue", 400)

    # Add label
    issue.labels.append(label)
    db.session.commit()

    return jsonify({"message": "Label added successfully"}), 200


@bp.route("/<int:id>/labels/<int:label_id>", methods=["DELETE"])
@login_required
@license_required("enterprise")
@resource_role_required("operator")
def remove_issue_label(id: int, label_id: int):
    """
    Remove a label from an issue.

    Requires operator role on the resource.

    Path Parameters:
        - id: Issue ID
        - label_id: Label ID

    Returns:
        204: Label removed
        403: License required or insufficient permissions
        404: Issue or label not found

    Example:
        DELETE /api/v1/issues/1/labels/2
    """
    issue = get_or_404(Issue, id)
    label = get_or_404(IssueLabel, label_id)

    # Remove label if present
    if label in issue.labels:
        issue.labels.remove(label)
        db.session.commit()

    return "", 204


# ============================================================================
# Entity Links Endpoints
# ============================================================================


@bp.route("/<int:id>/links", methods=["GET"])
@login_required
@license_required("enterprise")
def list_issue_entity_links(id: int):
    """
    List all entity links for an issue.

    Path Parameters:
        - id: Issue ID

    Returns:
        200: List of entity links
        403: License required
        404: Issue not found

    Example:
        GET /api/v1/issues/1/links
    """
    issue = get_or_404(Issue, id)

    # Serialize links
    schema = IssueEntityLinkSchema(many=True)
    return jsonify(schema.dump(issue.entity_links)), 200


@bp.route("/<int:id>/links", methods=["POST"])
@login_required
@license_required("enterprise")
@resource_role_required("operator")
def create_issue_entity_link(id: int):
    """
    Link an entity to an issue.

    Requires operator role on the resource.

    Path Parameters:
        - id: Issue ID

    Request Body:
        {
            "entity_id": 42,
            "link_type": "fixes"
        }

    Returns:
        201: Link created
        400: Invalid request
        403: License required or insufficient permissions
        404: Issue or entity not found

    Example:
        POST /api/v1/issues/1/links
    """
    issue = get_or_404(Issue, id)

    # Validate request
    create_schema = IssueEntityLinkCreateSchema()
    try:
        data = create_schema.load(request.get_json())
    except ValidationError as e:
        return make_error_response(str(e.messages), 400)

    # Verify entity exists
    from apps.api.models import Entity
    entity = get_or_404(Entity, data["entity_id"])

    # Check if link already exists
    existing = (
        db.session.query(IssueEntityLink)
        .filter_by(issue_id=issue.id, entity_id=entity.id, link_type=IssueLinkType(data["link_type"]))
        .first()
    )

    if existing:
        return make_error_response("Link already exists", 400)

    # Create link
    link = IssueEntityLink(
        issue_id=issue.id,
        entity_id=entity.id,
        link_type=IssueLinkType(data["link_type"]),
    )

    db.session.add(link)
    db.session.commit()

    # Serialize response
    schema = IssueEntityLinkSchema()
    return jsonify(schema.dump(link)), 201


@bp.route("/<int:id>/links/<int:link_id>", methods=["DELETE"])
@login_required
@license_required("enterprise")
@resource_role_required("operator")
def delete_issue_entity_link(id: int, link_id: int):
    """
    Remove an entity link from an issue.

    Requires operator role on the resource.

    Path Parameters:
        - id: Issue ID
        - link_id: Link ID

    Returns:
        204: Link deleted
        403: License required or insufficient permissions
        404: Issue or link not found

    Example:
        DELETE /api/v1/issues/1/links/3
    """
    issue = get_or_404(Issue, id)
    link = get_or_404(IssueEntityLink, link_id)

    # Verify link belongs to issue
    if link.issue_id != issue.id:
        return make_error_response("Link does not belong to this issue", 400)

    # Delete link
    db.session.delete(link)
    db.session.commit()

    return "", 204
