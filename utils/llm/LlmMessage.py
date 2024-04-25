from typing import Union


class LlmMessage:
    _role: Union[str, None]
    _content: Union[str, None]

    def __init__(self, parameters: dict = None, **kwargs):
        if parameters is not None:
            self._role = parameters.get('role', None)
            self._content = parameters.get('content', None)
        else:
            self._role = kwargs.get('role', "user")
            self._content = kwargs.get('content', None)

    @property
    def role(self) -> Union[str, None]:
        return self._role

    @property
    def content(self) -> Union[str, None]:
        return self._content


    def __eq__(self, other: 'LlmMessage') -> bool:
        if not isinstance(other, LlmMessage):
            return NotImplemented
        return (
                self._role == other._role and
                self._content == other._content
        )

    def __hash__(self) -> int:
        return hash((self._role, self._content))

    def __str__(self) -> str:
        return f"LlmMessage(role={self._role}, content={self._content})"

    def __repr__(self) -> str:
        return f"LlmMessage(role={self._role!r}, content={self._content!r})"

    def to_dict(self, system_role_name="user"):
        if self._role == "system":
            return {
                "role": system_role_name,
                "content": self._content
            }
        return {
            "role": self._role,
            "content": self._content
        }

    def __copy__(self):
        return LlmMessage(role=self.role, content=self.content)
