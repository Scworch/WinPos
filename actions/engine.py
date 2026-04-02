"""Action execution engine."""

from __future__ import annotations

import logging
from typing import Dict, List

from actions.base import Action, ActionContext, ActionResult
from actions.primitives import ACTION_REGISTRY
from config.models import ActionSpec
from utils.retry import retry_async


class ActionEngine:
    """Executes action chains with conditions, retries, and fallbacks."""

    def __init__(self) -> None:
        self._registry: Dict[str, Action] = ACTION_REGISTRY

    async def execute_chain(self, actions: List[ActionSpec], ctx: ActionContext) -> List[ActionResult]:
        results: List[ActionResult] = []
        logger = logging.getLogger(ctx.logger_name)

        for spec in actions:
            if spec.type == "use_chain":
                chain_name = spec.params.get("name")
                chain = ctx.config.action_chains.get(chain_name, [])
                logger.info("Executing chain '%s'", chain_name)
                results.extend(await self.execute_chain(chain, ctx))
                continue

            if not _evaluate_when(spec, ctx):
                logger.info("Skipping action '%s' due to condition", spec.type)
                continue

            action = self._registry.get(spec.type)
            if not action:
                results.append(ActionResult(False, message=f"Unknown action: {spec.type}"))
                continue

            async def run_action() -> ActionResult:
                return await action.run(ctx, spec)

            try:
                if spec.retry:
                    retries = int(spec.retry.get("retries", 1))
                    delay_s = float(spec.retry.get("delay_s", 0.5))
                    result = await retry_async(run_action, retries=retries, delay_s=delay_s)
                else:
                    result = await run_action()
            except Exception as exc:  # noqa: BLE001
                logger.exception("Action '%s' failed", spec.type)
                result = ActionResult(False, message=str(exc))

            results.append(result)

            if not result.success and spec.on_failure:
                logger.warning("Action '%s' failed; running fallback", spec.type)
                results.extend(await self.execute_chain(spec.on_failure, ctx))

        return results


def _evaluate_when(spec: ActionSpec, ctx: ActionContext) -> bool:
    if not spec.when:
        return True
    kind = spec.when.get("type")
    if kind == "process_running":
        return ctx.launcher.is_running(ctx.app)
    if kind == "window_exists":
        return bool(ctx.window_manager.find_windows(ctx.app.window_match))
    return True
