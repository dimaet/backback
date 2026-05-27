from copy import deepcopy
from typing import Optional


def best_subset(cuts, stock_length, kerf):
    """
    Подбор набора отрезков с максимальной суммой <= stock_length
    с учётом толщины лезвия (kerf)
    Использует оптимизированный алгоритм с ограничением глубины для больших наборов
    """
    
    if not cuts:
        return []
    
    # Ограничение: если отрезков больше 25, используем жадный алгоритм
    # чтобы избежать экспоненциального роста времени выполнения
    MAX_CUTS_FOR_BACKTRACK = 25
    
    if len(cuts) > MAX_CUTS_FOR_BACKTRACK:
        # Используем жадный алгоритм First Fit Decreasing
        return greedy_pack(cuts, stock_length, kerf)
    
    # Для небольших наборов используем точный backtracking
    best_sum = 0
    best_combo = []
    cuts_sorted = sorted(cuts, key=lambda x: -x["length"])

    def backtrack(index, current_sum, combo, depth=0):
        nonlocal best_sum, best_combo
        
        # Ограничение глубины рекурсии для безопасности
        if depth > 50:
            return

        effective_sum = current_sum + kerf * len(combo)
        if effective_sum > stock_length:
            return

        if effective_sum > best_sum:
            best_sum = effective_sum
            best_combo = combo[:]

        if index >= len(cuts_sorted):
            return

        # Pruning: если оставшиеся не могут улучшить результат
        remaining_sum = current_sum + sum(c["length"] for c in cuts_sorted[index:])
        if remaining_sum + kerf * (len(combo) + len(cuts_sorted) - index) <= best_sum:
            return

        # взять текущий (если помещается)
        if effective_sum + cuts_sorted[index]["length"] + kerf <= stock_length:
            backtrack(
                index + 1,
                current_sum + cuts_sorted[index]["length"],
                combo + [cuts_sorted[index]],
                depth + 1
            )

        # не брать
        backtrack(index + 1, current_sum, combo, depth + 1)

    backtrack(0, 0, [])
    return best_combo


def greedy_pack(cuts, stock_length, kerf):
    """
    Жадный алгоритм упаковки (First Fit Decreasing)
    Быстрее, но не всегда оптимален
    """
    result = []
    remaining_space = stock_length
    cuts_sorted = sorted(cuts, key=lambda x: -x["length"])
    
    for cut in cuts_sorted:
        cut_total = cut["length"] + kerf
        if cut_total <= remaining_space:
            result.append(cut)
            remaining_space -= cut_total
            
    return result


def optimize_cut(stocks: list, cuts: list, settings: Optional[dict] = None):
    """
    SmartCut-подобный линейный раскрой
    Поддержка:
    - толщина лезвия (kerf)
    - торцовка (trimming)
    """
    if not stocks:
        raise ValueError("Список заготовок не может быть пустым")
    if not cuts:
        raise ValueError("Список отрезков не может быть пустым")

    settings = settings or {}
    kerf = max(0, settings.get("kerf", 0))  # Убеждаемся, что kerf >= 0
    trimming = max(0, settings.get("trimming", 0))  # Убеждаемся, что trimming >= 0

    # Получаем уникальные материалы, используя "default" если материал не указан
    materials = set()
    for s in stocks:
        materials.add(s.get("material", "default"))
    for c in cuts:
        materials.add(c.get("material", "default"))

    result = {
        "materials": {},
        "total_waste_percent": 0
    }

    total_stock_length = 0
    total_waste_length = 0

    for material in materials:
        material_stocks = [s for s in stocks if s.get("material", "default") == material]
        material_cuts = [c for c in cuts if c.get("material", "default") == material]

        # --- заготовки ---
        expanded_stocks = []
        for s in material_stocks:
            for _ in range(s.get("quantity", 1)):
                effective_length = max(0, s["length"] - trimming)
                expanded_stocks.append({
                    "length": effective_length,
                    "original_length": s["length"],
                    "remaining": effective_length,
                    "name": s["name"],
                    "priority": s.get("priority", 0),
                    "cuts": []
                })

        expanded_stocks.sort(key=lambda x: (x["priority"], -x["length"]))

        # --- отрезки ---
        expanded_cuts = []
        for c in material_cuts:
            for _ in range(c.get("quantity", 1)):
                expanded_cuts.append({
                    "length": c["length"],
                    "name": c["name"]
                })

        # Используем список индексов для отслеживания использованных отрезков
        used_indices = set()
        remaining_cuts_list = list(enumerate(expanded_cuts))

        # --- основной алгоритм ---
        for stock_idx, stock in enumerate(expanded_stocks):
            # Получаем список неиспользованных отрезков
            available_cuts = [cut for idx, cut in remaining_cuts_list if idx not in used_indices]
            
            if not available_cuts:
                break

            # Логирование прогресса для больших наборов
            if len(expanded_stocks) > 50 and stock_idx % 10 == 0:
                import logging
                logger = logging.getLogger(__name__)
                logger.info(f"Обработка заготовки {stock_idx + 1}/{len(expanded_stocks)}")

            combo = best_subset(available_cuts, stock["length"], kerf)
            if not combo:
                continue

            total_cut_len = sum(c["length"] for c in combo)
            kerf_loss = kerf * len(combo)

            stock["cuts"] = combo
            stock["remaining"] = stock["length"] - total_cut_len - kerf_loss

            # Помечаем использованные отрезки
            for combo_cut in combo:
                for idx, cut in remaining_cuts_list:
                    if idx not in used_indices:
                        # Сравниваем по длине и имени
                        if (cut["length"] == combo_cut["length"] and 
                            cut.get("name") == combo_cut.get("name")):
                            used_indices.add(idx)
                            break
        
        # Получаем неиспользованные отрезки для результата
        remaining_cuts = [cut for idx, cut in remaining_cuts_list if idx not in used_indices]

        used_stocks = [s for s in expanded_stocks if s["cuts"]]
        unused_stocks = [
            {"length": s["original_length"], "name": s["name"]}
            for s in expanded_stocks if not s["cuts"]
        ]

        material_stock_length = sum(s["original_length"] for s in used_stocks)
        material_waste_length = sum(s["remaining"] for s in used_stocks)

        waste_percent = (
            round(material_waste_length / material_stock_length * 100, 2)
            if material_stock_length > 0 else 0
        )

        total_stock_length += material_stock_length
        total_waste_length += material_waste_length

        result["materials"][material] = {
            "used_stocks": len(used_stocks),
            "used_cuts": sum(len(s["cuts"]) for s in used_stocks),
            "waste_percent": waste_percent,
            "stocks": used_stocks,
            "unused_cuts": remaining_cuts,
            "unused_stocks": unused_stocks
        }

    result["total_waste_percent"] = (
        round(total_waste_length / total_stock_length * 100, 2)
        if total_stock_length > 0 else 0
    )

    # Убеждаемся, что все числовые значения валидны
    if not isinstance(result["total_waste_percent"], (int, float)):
        result["total_waste_percent"] = 0

    return result



