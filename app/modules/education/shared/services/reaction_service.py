from typing import Optional

from sqlmodel import Session, func, select

from app.modules.education.shared.model import (
    ReactionType,
    UserReaction,
)


class ReactionService:
    """Reusable service for handling user reactions on any content"""

    def get_user_reaction(
        self,
        session: Session,
        user_id: int,
        content_slug: str,
    ) -> Optional[UserReaction]:
        """Get existing reaction for a user on specific content"""
        statement = select(UserReaction).where(
            UserReaction.user_id == user_id,
            UserReaction.content_slug == content_slug,
        )
        return session.exec(statement).first()

    def toggle_reaction(
        self,
        session: Session,
        user_id: int,
        content_slug: str,
        reaction_type: ReactionType,
    ) -> dict:
        """
        Toggle a reaction. Returns dict with action taken and current reaction state.
        - If no reaction exists: create it
        - If same reaction exists: remove it (toggle off)
        - If different reaction exists: switch it
        """
        existing = self.get_user_reaction(session, user_id, content_slug)
        result = {"action": None, "current_reaction": None, "previous_reaction": None}

        if existing:
            result["previous_reaction"] = existing.reaction.value
            if existing.reaction == reaction_type:
                # Same reaction → remove (toggle off)
                session.delete(existing)
                result["action"] = "removed"
                result["current_reaction"] = None
            else:
                # Different reaction → switch
                existing.reaction = reaction_type
                session.add(existing)
                result["action"] = "switched"
                result["current_reaction"] = reaction_type.value
        else:
            # No reaction → create new
            new_reaction = UserReaction(
                user_id=user_id,
                content_slug=content_slug,
                reaction=reaction_type,
            )
            session.add(new_reaction)
            result["action"] = "added"
            result["current_reaction"] = reaction_type.value

        session.commit()
        return result

    def get_reaction_counts(
        self,
        session: Session,
        content_slug: str,
    ) -> dict:
        """Get like/dislike counts for specific content"""
        statement = (
            select(UserReaction.reaction, func.count(UserReaction.id))
            .where(UserReaction.content_slug == content_slug)
            .group_by(UserReaction.reaction)
        )
        results = session.exec(statement).all()

        counts = {"likes": 0, "dislikes": 0}
        for reaction, count in results:
            if reaction == ReactionType.LIKE:
                counts["likes"] = count
            elif reaction == ReactionType.DISLIKE:
                counts["dislikes"] = count

        return counts
