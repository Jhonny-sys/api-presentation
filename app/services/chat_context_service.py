from datetime import date

from app.schemas.experience import Experience
from app.schemas.portfolio import Portfolio
from app.services.portfolio_i18n_sync import _entity_slug

CURRENT_LABEL: dict[str, str] = {
    "es": "Actualmente",
    "en": "Currently",
    "pt": "Atualmente",
}

NO_DATES_LABEL: dict[str, str] = {
    "es": "Sin fechas",
    "en": "No dates",
    "pt": "Sem datas",
}

TECH_CATEGORY_LABEL: dict[str, dict[str, str]] = {
    "es": {
        "backend": "Backend",
        "frontend": "Frontend",
        "database": "Base de datos",
        "cloud": "Cloud",
        "other": "Otros",
    },
    "en": {
        "backend": "Backend",
        "frontend": "Frontend",
        "database": "Database",
        "cloud": "Cloud",
        "other": "Other",
    },
    "pt": {
        "backend": "Backend",
        "frontend": "Frontend",
        "database": "Banco de dados",
        "cloud": "Cloud",
        "other": "Outros",
    },
}

TECH_CATEGORY_ORDER = ("backend", "frontend", "database", "cloud", "other")

STACK_SECTION_HINT: dict[str, str] = {
    "es": (
        "Nota: preguntas generales sobre proyectos, stack o herramientas "
        "pueden usar esta sección; para bases de datos o cloud/host usa las secciones dedicadas abajo."
    ),
    "en": (
        "Note: general questions about projects, stack or tools "
        "may use this section; for databases or cloud/hosting use the dedicated sections below."
    ),
    "pt": (
        "Nota: perguntas gerais sobre projetos, stack ou ferramentas "
        "podem usar esta seção; para bancos de dados ou cloud/host use as seções dedicadas abaixo."
    ),
}

DATABASE_SECTION_HINT: dict[str, str] = {
    "es": (
        "Responde con esta sección cuando pregunten por bases de datos, DB, SQL, datos, "
        "MongoDB, PostgreSQL, MySQL, Supabase, Redis, etc."
    ),
    "en": (
        "Answer using this section when they ask about databases, DB, SQL, data stores, "
        "MongoDB, PostgreSQL, MySQL, Supabase, Redis, etc."
    ),
    "pt": (
        "Responda com esta seção quando perguntarem sobre bancos de dados, DB, SQL, dados, "
        "MongoDB, PostgreSQL, MySQL, Supabase, Redis, etc."
    ),
}

CLOUD_SECTION_HINT: dict[str, str] = {
    "es": (
        "Responde con esta sección cuando pregunten por host, hosting, cloud, nube, deploy, "
        "despliegue, infraestructura, AWS, GCP, Azure, Vercel, Render, Fly.io, Docker, Kubernetes, etc."
    ),
    "en": (
        "Answer using this section when they ask about host, hosting, cloud, deploy, "
        "infrastructure, AWS, GCP, Azure, Vercel, Render, Fly.io, Docker, Kubernetes, etc."
    ),
    "pt": (
        "Responda com esta seção quando perguntarem sobre host, hosting, cloud, deploy, "
        "infraestrutura, AWS, GCP, Azure, Vercel, Render, Fly.io, Docker, Kubernetes, etc."
    ),
}

EMPTY_CATEGORY_LABEL: dict[str, str] = {
    "es": "(Sin tecnologías registradas en esta categoría)",
    "en": "(No technologies registered in this category)",
    "pt": "(Sem tecnologias registradas nesta categoria)",
}


def _localized(messages: dict[str, str], key: str, fallback: str | None) -> str:
    return messages.get(key) or fallback or ""


def _experience_key(entity_id, field: str) -> str:
    return f"experience.{_entity_slug(entity_id)}.{field}"


def _study_key(entity_id, field: str) -> str:
    return f"studies.{_entity_slug(entity_id)}.{field}"


def _technology_key(entity_id, field: str) -> str:
    return f"technologies.{_entity_slug(entity_id)}.{field}"


def _months_between(start: date, end: date) -> int:
    return max(0, (end.year - start.year) * 12 + (end.month - start.month))


def _job_end(item: Experience) -> date:
    if item.is_current:
        return date.today()
    return item.end_date or date.today()


def _format_duration(months: int, lang: str) -> str:
    years, rem = divmod(months, 12)
    if lang == "en":
        parts = []
        if years:
            parts.append(f"{years} year{'s' if years != 1 else ''}")
        if rem:
            parts.append(f"{rem} month{'s' if rem != 1 else ''}")
        return " and ".join(parts) or "0 months"
    if lang == "pt":
        parts = []
        if years:
            parts.append(f"{years} ano{'s' if years != 1 else ''}")
        if rem:
            parts.append(f"{rem} mes{'es' if rem != 1 else ''}")
        return " e ".join(parts) or "0 meses"
    parts = []
    if years:
        parts.append(f"{years} año{'s' if years != 1 else ''}")
    if rem:
        parts.append(f"{rem} mes{'es' if rem != 1 else ''}")
    return " y ".join(parts) or "0 meses"


def _experience_summary(experiences: list[Experience], lang: str) -> str:
    if not experiences:
        return ""

    today = date.today()
    earliest = min(item.start_date for item in experiences)
    latest = max(_job_end(item) for item in experiences)
    career_months = _months_between(earliest, latest)
    total_job_months = sum(_months_between(item.start_date, _job_end(item)) for item in experiences)

    if lang == "en":
        return (
            f"Summary: {len(experiences)} registered roles. "
            f"Career from {earliest} to {latest} ({_format_duration(career_months, lang)}). "
            f"Combined time in listed roles: {_format_duration(total_job_months, lang)}."
        )
    if lang == "pt":
        return (
            f"Resumo: {len(experiences)} cargos registrados. "
            f"Carreira de {earliest} a {latest} ({_format_duration(career_months, lang)}). "
            f"Tempo combinado nos cargos listados: {_format_duration(total_job_months, lang)}."
        )
    return (
        f"Resumen: {len(experiences)} empleos registrados. "
        f"Trayectoria desde {earliest} hasta {latest} ({_format_duration(career_months, lang)}). "
        f"Tiempo acumulado en los cargos listados: {_format_duration(total_job_months, lang)}."
    )


def _company_key(company: str) -> str:
    return " ".join(company.casefold().split())


def _experience_by_company_summary(
    experiences: list[Experience],
    messages: dict[str, str],
    lang: str,
) -> list[str]:
    """Build explicit company aggregates so the assistant considers every role."""
    grouped: dict[str, list[Experience]] = {}
    for item in experiences:
        grouped.setdefault(_company_key(item.company), []).append(item)

    lines: list[str] = []
    for items in grouped.values():
        if len(items) < 2:
            continue
        company = _localized(
            messages,
            _experience_key(items[0].id, "company"),
            items[0].company,
        ).strip()
        total_months = sum(
            _months_between(item.start_date, _job_end(item)) for item in items
        )
        periods = "; ".join(
            _period_label(item.start_date, item.end_date, item.is_current, lang)
            for item in items
        )
        if lang == "en":
            lines.append(
                f"- {company}: {len(items)} registered roles; combined time "
                f"{_format_duration(total_months, lang)}. Periods: {periods}."
            )
        elif lang == "pt":
            lines.append(
                f"- {company}: {len(items)} cargos registrados; tempo combinado "
                f"de {_format_duration(total_months, lang)}. Períodos: {periods}."
            )
        else:
            lines.append(
                f"- {company}: {len(items)} cargos registrados; tiempo acumulado "
                f"de {_format_duration(total_months, lang)}. Períodos: {periods}."
            )
    return lines


def _period_label(
    start: date | str | None,
    end: date | str | None,
    is_current: bool,
    lang: str,
) -> str:
    start_s = str(start) if start else None
    end_s = str(end) if end else None
    current = CURRENT_LABEL.get(lang, CURRENT_LABEL["es"])
    no_dates = NO_DATES_LABEL.get(lang, NO_DATES_LABEL["es"])
    if not start_s and not end_s:
        return current if is_current else no_dates
    end_label = current if is_current else (end_s or "")
    return f"{start_s} — {end_label}" if start_s else end_label


def _tech_category_label(category: str, lang: str) -> str:
    labels = TECH_CATEGORY_LABEL.get(lang, TECH_CATEGORY_LABEL["es"])
    return labels.get(category, labels["other"])


def _group_technologies_by_category(technologies):
    buckets: dict[str, list] = {}
    for item in technologies:
        category = item.category if item.category in TECH_CATEGORY_ORDER else "other"
        buckets.setdefault(category, []).append(item)

    groups: list[tuple[str, list]] = []
    for category in TECH_CATEGORY_ORDER:
        if category in buckets:
            groups.append((category, buckets[category]))
    return groups


def _technologies_by_category(technologies, category: str) -> list:
    return [
        item
        for item in technologies
        if (item.category if item.category in TECH_CATEGORY_ORDER else "other") == category
    ]


def _format_technology_lines(items, messages: dict[str, str], lang: str) -> list[str]:
    if not items:
        empty = EMPTY_CATEGORY_LABEL.get(lang, EMPTY_CATEGORY_LABEL["es"])
        return [f"- {empty}"]

    lines: list[str] = []
    for item in items:
        description = _localized(
            messages,
            _technology_key(item.id, "description"),
            item.description,
        )
        line = f"- {item.name}"
        if description:
            line += f": {description}"
        lines.append(line)
    return lines


def _append_technology_category_section(
    sections: list[str],
    *,
    title: str,
    hint: str,
    items,
    messages: dict[str, str],
    lang: str,
) -> None:
    sections.append(title)
    sections.append(hint)
    sections.extend(_format_technology_lines(items, messages, lang))
    sections.append("")


def build_portfolio_context(portfolio: Portfolio, messages: dict[str, str], lang: str) -> str:
    profile = portfolio.profile
    sections: list[str] = [f"Idioma de respuesta: {lang}", ""]

    if profile:
        headline = _localized(messages, "profile.headline", profile.headline)
        bio = _localized(messages, "profile.bio", profile.bio)
        sections.extend(
            [
                "## Perfil (hoja de vida, CV, bio, presentación, idiomas)",
                "Usa esta sección cuando pregunten por el perfil, hoja de vida, CV, quién es o qué idiomas habla.",
                f"Nombre: {profile.full_name}",
                f"Título: {headline}",
                f"Bio: {bio}",
            ]
        )
        if profile.email:
            sections.append(f"Email: {profile.email}")
        if profile.phone:
            sections.append(f"Teléfono: {profile.phone}")
        if profile.location:
            sections.append(f"Ubicación: {profile.location}")
        if profile.languages:
            sections.append(f"Idiomas que habla: {profile.languages}")
        social = profile.social_links
        if social.github:
            sections.append(f"GitHub: {social.github}")
        if social.linkedin:
            sections.append(f"LinkedIn: {social.linkedin}")
        sections.append("")

    if portfolio.experience:
        sections.append("## Experiencia laboral")
        sections.append(_experience_summary(portfolio.experience, lang))
        company_summaries = _experience_by_company_summary(
            portfolio.experience, messages, lang
        )
        if company_summaries:
            sections.append("### Resumen por empresa")
            sections.append(
                "Si preguntan por una empresa, usa todas sus entradas y el tiempo acumulado; "
                "no respondas usando solo un cargo."
            )
            sections.extend(company_summaries)
        for item in portfolio.experience:
            period = _period_label(item.start_date, item.end_date, item.is_current, lang)
            months = _months_between(item.start_date, _job_end(item))
            duration = _format_duration(months, lang)
            company = _localized(messages, _experience_key(item.id, "company"), item.company)
            description = _localized(
                messages,
                _experience_key(item.id, "description"),
                item.description,
            )
            role = item.role.strip() if item.role else ""
            title = company.strip()
            if role and role.lower() not in title.lower():
                title = f"{title} — {role}"
            block = [f"- {title} ({period}, {duration})"]
            if description:
                block.append(f"  {description}")
            sections.extend(block)
        sections.append("")

    if portfolio.studies:
        sections.append("## Estudios")
        for item in portfolio.studies:
            period = _period_label(item.start_date, item.end_date, item.is_current, lang)
            degree = _localized(messages, _study_key(item.id, "degree"), item.degree)
            institution = _localized(
                messages,
                _study_key(item.id, "institution"),
                item.institution,
            )
            sections.append(f"- {degree} — {institution} ({period})")
        sections.append("")

    if portfolio.technologies:
        db_items = _technologies_by_category(portfolio.technologies, "database")
        cloud_items = _technologies_by_category(portfolio.technologies, "cloud")
        stack_items = [
            item
            for item in portfolio.technologies
            if (item.category if item.category in TECH_CATEGORY_ORDER else "other")
            not in ("database", "cloud")
        ]

        _append_technology_category_section(
            sections,
            title="## Bases de datos",
            hint=DATABASE_SECTION_HINT.get(lang, DATABASE_SECTION_HINT["es"]),
            items=db_items,
            messages=messages,
            lang=lang,
        )
        _append_technology_category_section(
            sections,
            title="## Cloud y hosting",
            hint=CLOUD_SECTION_HINT.get(lang, CLOUD_SECTION_HINT["es"]),
            items=cloud_items,
            messages=messages,
            lang=lang,
        )

        if stack_items:
            hint = STACK_SECTION_HINT.get(lang, STACK_SECTION_HINT["es"])
            sections.append("## Stack tecnológico (backend, frontend y otros)")
            sections.append(hint)
            for category, items in _group_technologies_by_category(stack_items):
                sections.append(f"### {_tech_category_label(category, lang)}")
                sections.extend(_format_technology_lines(items, messages, lang))
            sections.append("")

    return "\n".join(sections).strip()
