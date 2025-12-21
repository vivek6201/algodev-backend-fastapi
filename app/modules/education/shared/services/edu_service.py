from sqlmodel import Session, select

from app.modules.education.shared.model import (
    CategoriesBase,
    EducationCategory,
)


class EducationService:
    def get_category(self, session: Session, category_id: int):
        try:
            return session.get(EducationCategory, category_id)
        except Exception as e:
            raise e

    def get_categories(self, session: Session):
        try:
            return session.exec(select(EducationCategory)).all()
        except Exception as e:
            raise e

    def create_category(self, session: Session, category_data: CategoriesBase):
        try:
            category = EducationCategory(**category_data.dict())
            session.add(category)
            session.commit()
            session.refresh(category)
            return category
        except Exception as e:
            raise e

    def update_category(self, session: Session, category_id: int, category_data: CategoriesBase):
        try:
            category = self.get_category(session=session, category_id=category_id)

            if not category:
                return None

            category.name = category_data.name
            session.add(category)
            session.commit()
            session.refresh(category)
            return category
        except Exception as e:
            raise e

    def delete_category(self, session: Session, category_id: int):
        pass
