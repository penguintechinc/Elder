"""Organization API endpoints using PyDAL."""

from flask import Blueprint, request, jsonify, current_app
from datetime import datetime, timezone

bp = Blueprint("organizations", __name__)


@bp.route("", methods=["GET"])
def list_organizations():
    """
    List all organizations with pagination and filtering.

    Query Parameters:
        - page: Page number (default: 1)
        - per_page: Items per page (default: 50, max: 1000)
        - parent_id: Filter by parent organization ID
        - name: Filter by name (partial match)

    Returns:
        200: List of organizations with pagination metadata
    """
    db = current_app.db

    # Get pagination params
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 50, type=int), 1000)

    # Build query
    query = db.organizations.id > 0

    # Apply filters
    if request.args.get("parent_id"):
        parent_id = request.args.get("parent_id", type=int)
        query &= (db.organizations.parent_id == parent_id)

    if request.args.get("name"):
        name = request.args.get("name")
        query &= (db.organizations.name.contains(name))

    # Get total count
    total = db(query).count()

    # Calculate pagination
    offset = (page - 1) * per_page
    pages = (total + per_page - 1) // per_page if total > 0 else 0

    # Get paginated results
    rows = db(query).select(
        orderby=db.organizations.name,
        limitby=(offset, offset + per_page)
    )

    # Convert to dict list
    items = []
    for row in rows:
        items.append({
            'id': row.id,
            'name': row.name,
            'description': row.description,
            'parent_id': row.parent_id,
            'ldap_dn': row.ldap_dn,
            'saml_group': row.saml_group,
            'owner_identity_id': row.owner_identity_id,
            'owner_group_id': row.owner_group_id,
            'created_at': row.created_at.isoformat() if row.created_at else None,
            'updated_at': row.updated_at.isoformat() if row.updated_at else None,
        })

    return jsonify({
        'items': items,
        'total': total,
        'page': page,
        'per_page': per_page,
        'pages': pages,
    }), 200


@bp.route("", methods=["POST"])
def create_organization():
    """
    Create a new organization.

    Request Body:
        JSON object with organization fields

    Returns:
        201: Created organization
        400: Validation error
    """
    db = current_app.db
    data = request.get_json() or {}

    # Validate required fields
    if not data.get('name'):
        return jsonify({'error': 'Name is required'}), 400

    # Insert organization
    try:
        org_id = db.organizations.insert(
            name=data.get('name'),
            description=data.get('description'),
            parent_id=data.get('parent_id'),
            ldap_dn=data.get('ldap_dn'),
            saml_group=data.get('saml_group'),
            owner_identity_id=data.get('owner_identity_id'),
            owner_group_id=data.get('owner_group_id'),
        )
        db.commit()

        # Fetch and return created org
        org = db.organizations[org_id]
        return jsonify({
            'id': org.id,
            'name': org.name,
            'description': org.description,
            'parent_id': org.parent_id,
            'ldap_dn': org.ldap_dn,
            'saml_group': org.saml_group,
            'owner_identity_id': org.owner_identity_id,
            'owner_group_id': org.owner_group_id,
            'created_at': org.created_at.isoformat() if org.created_at else None,
            'updated_at': org.updated_at.isoformat() if org.updated_at else None,
        }), 201

    except Exception as e:
        db.rollback()
        return jsonify({'error': f'Database error: {str(e)}'}), 500


@bp.route("/<int:id>", methods=["GET"])
def get_organization(id: int):
    """
    Get a single organization by ID.

    Path Parameters:
        - id: Organization ID

    Returns:
        200: Organization details
        404: Organization not found
    """
    db = current_app.db

    org = db.organizations[id]
    if not org:
        return jsonify({'error': 'Organization not found'}), 404

    return jsonify({
        'id': org.id,
        'name': org.name,
        'description': org.description,
        'parent_id': org.parent_id,
        'ldap_dn': org.ldap_dn,
        'saml_group': org.saml_group,
        'owner_identity_id': org.owner_identity_id,
        'owner_group_id': org.owner_group_id,
        'created_at': org.created_at.isoformat() if org.created_at else None,
        'updated_at': org.updated_at.isoformat() if org.updated_at else None,
    }), 200


@bp.route("/<int:id>", methods=["PATCH", "PUT"])
def update_organization(id: int):
    """
    Update an organization.

    Path Parameters:
        - id: Organization ID

    Request Body:
        JSON object with fields to update

    Returns:
        200: Updated organization
        404: Organization not found
    """
    db = current_app.db

    org = db.organizations[id]
    if not org:
        return jsonify({'error': 'Organization not found'}), 404

    data = request.get_json() or {}

    # Update fields
    update_fields = {}
    for field in ['name', 'description', 'parent_id', 'ldap_dn', 'saml_group', 'owner_identity_id', 'owner_group_id']:
        if field in data:
            update_fields[field] = data[field]

    if update_fields:
        try:
            db(db.organizations.id == id).update(**update_fields)
            db.commit()

            # Fetch updated org
            org = db.organizations[id]
            return jsonify({
                'id': org.id,
                'name': org.name,
                'description': org.description,
                'parent_id': org.parent_id,
                'ldap_dn': org.ldap_dn,
                'saml_group': org.saml_group,
                'owner_identity_id': org.owner_identity_id,
                'owner_group_id': org.owner_group_id,
                'created_at': org.created_at.isoformat() if org.created_at else None,
                'updated_at': org.updated_at.isoformat() if org.updated_at else None,
            }), 200

        except Exception as e:
            db.rollback()
            return jsonify({'error': f'Database error: {str(e)}'}), 500

    return jsonify({'error': 'No fields to update'}), 400


@bp.route("/<int:id>", methods=["DELETE"])
def delete_organization(id: int):
    """
    Delete an organization.

    Path Parameters:
        - id: Organization ID

    Returns:
        204: Organization deleted
        404: Organization not found
        400: Cannot delete organization with children
    """
    db = current_app.db

    org = db.organizations[id]
    if not org:
        return jsonify({'error': 'Organization not found'}), 404

    # Check if organization has children
    children_count = db((db.organizations.parent_id == id)).count()
    if children_count > 0:
        return jsonify({'error': 'Cannot delete organization with child organizations'}), 400

    try:
        del db.organizations[id]
        db.commit()
        return '', 204

    except Exception as e:
        db.rollback()
        return jsonify({'error': f'Database error: {str(e)}'}), 500
