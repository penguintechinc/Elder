"""Webhook notification utilities for Elder."""
# flake8: noqa: E501


from shared.webhooks.issue_webhooks import send_issue_created_webhooks

__all__ = ["send_issue_created_webhooks"]
