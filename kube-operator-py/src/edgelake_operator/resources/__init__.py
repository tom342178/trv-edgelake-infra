"""Resource builders for Kubernetes objects."""

from . import configmap, deployment, pvc, secret, service

__all__ = ["configmap", "deployment", "service", "pvc", "secret"]
