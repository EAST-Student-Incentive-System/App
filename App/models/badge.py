from App.database import db
from .student_badge import StudentBadge

class Badge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    points_required = db.Column(db.Integer, nullable=True)

    # NEW: badge type ("milestone" or "event_type")
    type = db.Column(db.String(32), nullable=False, default="milestone")

    student_badges = db.relationship(
        "StudentBadge",
        back_populates="badge",
        cascade="all, delete-orphan"
    )

    def get_json(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "pointsRequired": self.points_required,
            "type": self.type,
        }

    def __repr__(self):
        return (
            f"<Badge {self.id}: {self.name} - {self.description} "
            f"(Type: {self.type}, Points Required: {self.points_required})>"
        )

    def meets_requirements(self, student):
        # Milestones are point-based; event_type badges should be awarded by event logic, not points.
        if self.type == "event_type":
            return False
        return student.points >= self.points_required