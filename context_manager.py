from collections.abc import Iterable


class ContextManager:
    def __init__(self) -> None:
        self._contexts: dict[int, list[dict[str, str]]] = {}

    def get(self, user_id: int, system_prompt: str) -> list[dict[str, str]]:
        history = self._contexts.setdefault(user_id, [])
        return [{"role": "system", "content": system_prompt}, *history]

    def add(self, user_id: int, role: str, content: str) -> None:
        self._contexts.setdefault(user_id, []).append({"role": role, "content": content})

    def clear(self, user_id: int) -> None:
        self._contexts.pop(user_id, None)

    def message_count(self, user_id: int) -> int:
        return len(self._contexts.get(user_id, []))
