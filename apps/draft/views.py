import json

from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST
from django.core.serializers.json import DjangoJSONEncoder

from apps.meta.models import Hero, HeroCounter, HeroSynergy, Patch, TierEntry

TIER_SCORES = {"S": 5, "A": 4, "B": 3, "C": 2}
COUNTER_SCORES = {"hard": 3.0, "soft": 1.5}
SYNERGY_SCORES = {"strong": 2.0, "moderate": 1.0}
MOBILITY_SCORES = {"high": 1.0, "medium": 0.5, "low": 0.0}

ROLE_PRIMARY_BONUS = 1.5
ROLE_SECONDARY_BONUS = 0.75
DAMAGE_BALANCE_BONUS = 4.0
PHASE_BALANCE_BONUS = 3.0
CC_PER_HERO_BONUS = 1.5
SUSTAIN_BONUS = 4.0


def draft_page(request):
    heroes = Hero.objects.select_related("role", "secondary_role").order_by("name_ru")
    heroes_data = [
        {
            "id": h.pk,
            "name_ru": h.name_ru or h.name,
            "role_slug": h.role.slug if h.role else "",
            "role_name": h.role.name_ru if h.role else "",
            "icon_url": h.icon.url if h.icon else "",
        }
        for h in heroes
    ]
    roles = list(
        Hero.objects.filter(role__isnull=False)
        .values("role__slug", "role__name_ru")
        .distinct()
        .order_by("role__name_ru")
    )
    return render(request, "draft/index.html", {
        "heroes_json": json.dumps(heroes_data, cls=DjangoJSONEncoder),
        "roles": roles,
    })


@require_POST
def analyze(request):
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    team_a_ids = [int(i) for i in data.get("team_a", []) if i]
    team_b_ids = [int(i) for i in data.get("team_b", []) if i]

    if not team_a_ids or not team_b_ids:
        return JsonResponse({"error": "Обе команды должны содержать хотя бы одного героя"}, status=400)

    patch = Patch.objects.filter(is_current=True).first()

    team_a = list(Hero.objects.filter(pk__in=team_a_ids).select_related("role", "secondary_role"))
    team_b = list(Hero.objects.filter(pk__in=team_b_ids).select_related("role", "secondary_role"))

    result_a = _score_team(team_a, team_b, patch)
    result_b = _score_team(team_b, team_a, patch)

    total_a = result_a["total"]
    total_b = result_b["total"]
    total_sum = total_a + total_b
    advantage_pct = round(abs(total_a - total_b) / total_sum * 100) if total_sum > 0 else 0

    if total_a > total_b:
        winner = "a"
    elif total_b > total_a:
        winner = "b"
    else:
        winner = "draw"

    return JsonResponse({
        "team_a": result_a,
        "team_b": result_b,
        "winner": winner,
        "advantage_pct": advantage_pct,
    })


def _score_team(heroes, enemy_heroes, patch):
    hero_ids = [h.pk for h in heroes]
    enemy_ids = [h.pk for h in enemy_heroes]

    # 1. Мета-счёт
    hero_tiers = {}
    if patch and hero_ids:
        for e in TierEntry.objects.filter(hero__in=hero_ids, patch=patch):
            hero_tiers[e.hero_id] = e.tier
    meta_score = sum(TIER_SCORES.get(hero_tiers.get(h.pk), 0) for h in heroes)

    # 2. Покрытие ролей (первичная + вторичная)
    primary_roles = {h.role_id for h in heroes if h.role_id}
    secondary_roles = {h.secondary_role_id for h in heroes if h.secondary_role_id}
    all_roles = primary_roles | secondary_roles
    role_score = len(primary_roles) * ROLE_PRIMARY_BONUS + len(secondary_roles - primary_roles) * ROLE_SECONDARY_BONUS

    # 3. Контр-пики
    counter_score = 0.0
    if hero_ids and enemy_ids:
        for c in HeroCounter.objects.filter(countered_by__in=hero_ids, hero__in=enemy_ids):
            counter_score += COUNTER_SCORES[c.strength]

    # 4. Синергии
    synergy_score = 0.0
    if len(hero_ids) > 1:
        for s in HeroSynergy.objects.filter(Q(hero_a__in=hero_ids, hero_b__in=hero_ids)):
            synergy_score += SYNERGY_SCORES[s.strength]

    # 5. Баланс урона
    damage_types = {h.damage_type for h in heroes if h.damage_type}
    has_physical = bool(damage_types & {"physical", "mixed"})
    has_magic = bool(damage_types & {"magic", "mixed"})
    damage_score = DAMAGE_BALANCE_BONUS if (has_physical and has_magic) else 0.0

    # 6. Баланс фаз игры
    phases = {h.game_phase for h in heroes if h.game_phase}
    phase_score = PHASE_BALANCE_BONUS if ("early" in phases and "late" in phases) else 0.0

    # 7. CC присутствие
    cc_count = sum(1 for h in heroes if h.has_cc)
    cc_score = cc_count * CC_PER_HERO_BONUS

    # 8. Sustain
    sustain_score = SUSTAIN_BONUS if any(h.has_sustain for h in heroes) else 0.0

    # 9. Мобильность
    mobility_score = sum(MOBILITY_SCORES.get(h.mobility, 0.0) for h in heroes)

    total = (
        meta_score + role_score + counter_score + synergy_score +
        damage_score + phase_score + cc_score + sustain_score + mobility_score
    )

    return {
        "total": round(total, 1),
        "meta": meta_score,
        "roles": round(role_score, 1),
        "counters": round(counter_score, 1),
        "synergies": round(synergy_score, 1),
        "damage": damage_score,
        "phase": phase_score,
        "cc": round(cc_score, 1),
        "sustain": sustain_score,
        "mobility": round(mobility_score, 1),
        "hero_tiers": hero_tiers,
    }
