from sqlalchemy import delete, select

from shared.configs.db import db
from shared.models.course import Course
from shared.models.course_certificate_validity import CourseCertificateValidity
from shared.models.course_class_type import CourseClassType
from shared.models.course_related import CourseRelated
from shared.models.course_theme import CourseTheme
from shared.models.course_theme_detail import CourseThemeDetail
from shared.models.course_type import CourseType


class CourseRepository:
    def get_course(self, course_id: str) -> Course | None:
        return db.session.scalar(
            select(Course).where(
                (Course.id == course_id) & (Course.is_deleted == False)
            )
        )

    def is_slug_taken(self, slug: str, exclude_id: str | None = None) -> bool:
        query = select(Course.id).where(
            (Course.slug == slug) & (Course.is_deleted == False)
        )
        if exclude_id:
            query = query.where(Course.id != exclude_id)

        return db.session.scalar(query) is not None

    def get_type(self, option_id: str) -> CourseType | None:
        return db.session.scalar(
            select(CourseType).where(
                (CourseType.id == option_id) & (CourseType.is_deleted == False)
            )
        )

    def get_class_type(self, option_id: str) -> CourseClassType | None:
        return db.session.scalar(
            select(CourseClassType).where(
                (CourseClassType.id == option_id)
                & (CourseClassType.is_deleted == False)
            )
        )

    def get_certificate_validity(
        self, option_id: str
    ) -> CourseCertificateValidity | None:
        return db.session.scalar(
            select(CourseCertificateValidity).where(
                (CourseCertificateValidity.id == option_id)
                & (CourseCertificateValidity.is_deleted == False)
            )
        )

    def get_themes_by_sanity_ids(self, sanity_ids: list[str]) -> list[CourseTheme]:
        return list(
            db.session.scalars(
                select(CourseTheme).where(
                    (CourseTheme.sanity_id.in_(sanity_ids))
                    & (CourseTheme.is_deleted == False)
                )
            ).all()
        )

    def get_existing_course_ids(self, course_ids: list[str]) -> set[str]:
        return set(
            db.session.scalars(
                select(Course.id).where(
                    Course.id.in_(course_ids) & (Course.is_deleted == False)
                )
            ).all()
        )

    def replace_themes(self, course_id: str, theme_ids: list[str]) -> None:
        db.session.execute(
            delete(CourseThemeDetail).where(CourseThemeDetail.course_id == course_id)
        )
        for theme_id in theme_ids:
            db.save(CourseThemeDetail(course_id=course_id, course_theme_id=theme_id))

    def replace_related(self, course_id: str, related_ids: list[str]) -> None:
        db.session.execute(
            delete(CourseRelated).where(CourseRelated.course_id == course_id)
        )
        for related_id in related_ids:
            db.save(CourseRelated(course_id=course_id, course_related_id=related_id))
