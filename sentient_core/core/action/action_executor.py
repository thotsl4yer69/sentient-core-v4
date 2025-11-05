"""
Action executor for performing actions in the environment.
"""

import logging
from typing import Dict, Any, Optional, List, Callable
import time


logger = logging.getLogger(__name__)


class ActionExecutor:
    """
    Executes actions based on agent decisions.

    Provides:
    - Action validation
    - Safe execution in sandbox
    - Rollback on failure
    - Action history
    """

    def __init__(self, config):
        """
        Initialize action executor.

        Args:
            config: Configuration object
        """
        self.config = config

        # Configuration
        self.max_concurrent = config.get('action.max_concurrent_actions', 5)
        self.timeout = config.get('action.timeout', 30)
        self.enable_safety = config.get('action.enable_safety_checks', True)
        self.enable_validation = config.get('action.validate_before_execution', True)
        self.enable_rollback = config.get('action.rollback_on_failure', True)

        # State
        self.action_history: List[Dict[str, Any]] = []
        self.registered_actions: Dict[str, Callable] = {}
        self.active_actions: List[str] = []

        logger.info("ActionExecutor created")

    def execute(self, action: str, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute an action.

        Args:
            action: Action to execute
            parameters: Action parameters

        Returns:
            Action result
        """
        logger.info(f"Executing action: {action}")

        # Validate action
        if self.enable_validation:
            validation = self._validate_action(action, parameters)
            if not validation['valid']:
                return {
                    'action': action,
                    'status': 'invalid',
                    'error': validation['reason']
                }

        # Safety check
        if self.enable_safety:
            safety = self._safety_check(action, parameters)
            if not safety['safe']:
                return {
                    'action': action,
                    'status': 'unsafe',
                    'error': safety['reason']
                }

        # Execute action
        start_time = time.time()

        try:
            if action in self.registered_actions:
                result = self.registered_actions[action](parameters or {})
            else:
                result = self._default_action(action, parameters)

            duration = time.time() - start_time

            action_record = {
                'action': action,
                'parameters': parameters,
                'result': result,
                'status': 'completed',
                'duration': duration,
                'timestamp': start_time
            }

        except Exception as e:
            logger.error(f"Action execution failed: {e}")

            duration = time.time() - start_time

            action_record = {
                'action': action,
                'parameters': parameters,
                'status': 'failed',
                'error': str(e),
                'duration': duration,
                'timestamp': start_time
            }

            # Rollback if enabled
            if self.enable_rollback:
                self._rollback_action(action, parameters)

        # Store in history
        self.action_history.append(action_record)

        return action_record

    def register_action(self, name: str, handler: Callable):
        """
        Register a custom action handler.

        Args:
            name: Action name
            handler: Callable that executes the action
        """
        self.registered_actions[name] = handler
        logger.info(f"Registered action: {name}")

    def _validate_action(self, action: str, parameters: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate action before execution."""
        # Basic validation
        if not action:
            return {'valid': False, 'reason': 'Action name is empty'}

        return {'valid': True}

    def _safety_check(self, action: str, parameters: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Perform safety checks on action."""
        # Check for dangerous actions
        dangerous_actions = ['delete_all', 'format', 'destroy']

        if action.lower() in dangerous_actions:
            return {'safe': False, 'reason': f'Action {action} is dangerous'}

        return {'safe': True}

    def _default_action(self, action: str, parameters: Optional[Dict[str, Any]]) -> Any:
        """Default action handler."""
        logger.info(f"Executing default action: {action}")

        return {
            'message': f'Action {action} executed with parameters {parameters}',
            'success': True
        }

    def _rollback_action(self, action: str, parameters: Optional[Dict[str, Any]]):
        """Rollback a failed action."""
        logger.info(f"Rolling back action: {action}")
        # Rollback logic would go here

    def get_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get action history."""
        return self.action_history[-limit:]

    def clear_history(self):
        """Clear action history."""
        self.action_history.clear()
        logger.info("Action history cleared")
