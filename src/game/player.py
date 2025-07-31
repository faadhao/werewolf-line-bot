from .role import Role

class Player:
    def __init__(self, user_id: str, display_name: str):
        self.user_id = user_id
        self.display_name = display_name
        self.role = None
        self.is_ready = False
        self.voted_by = []

    def set_role(self, role: Role):
        self.role = role

    def is_alive(self) -> bool:
        return self.role and self.role.is_alive

    def toggle_ready(self):
        self.is_ready = not self.is_ready

    def add_vote(self, voter_id: str):
        self.voted_by.append(voter_id)

    def clear_votes(self):
        self.voted_by = []

    def get_vote_count(self) -> int:
        return len(self.voted_by)