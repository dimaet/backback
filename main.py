# main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from backend.algorithm import optimize_cut
import traceback
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Sheet Master API", version="1.0.0")

# ===== CORS =====
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # для диплома допустимо
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"status": "ok", "message": "Sheet Master API is running"}

@app.post("/optimize")
def optimize(data: dict):
    """
    data = {
        "stocks": [
            {
                "length": 6000,
                "quantity": 3,
                "name": "Труба 6м",
                "priority": 1,
                "material": "steel"
            }
        ],
        "cuts": [
            {
                "length": 1500,
                "quantity": 4,
                "name": "Отрезок A",
                "material": "steel"
            }
        ],
        "settings": {
            "kerf": 3,
            "trimming": 0
        }
    }
    """
    try:
        # Валидация входных данных
        if not isinstance(data, dict):
            raise HTTPException(status_code=400, detail="Данные должны быть объектом")
        
        stocks = data.get("stocks", [])
        cuts = data.get("cuts", [])
        settings = data.get("settings", {})
        
        if not isinstance(stocks, list) or not stocks:
            raise HTTPException(status_code=400, detail="Необходимо указать хотя бы одну заготовку в массиве 'stocks'")
        
        if not isinstance(cuts, list) or not cuts:
            raise HTTPException(status_code=400, detail="Необходимо указать хотя бы один отрезок в массиве 'cuts'")
        
        # Валидация заготовок
        for i, stock in enumerate(stocks):
            if not isinstance(stock, dict):
                raise HTTPException(status_code=400, detail=f"Заготовка #{i+1} должна быть объектом")
            if "length" not in stock or not isinstance(stock["length"], (int, float)) or stock["length"] <= 0:
                raise HTTPException(status_code=400, detail=f"Заготовка #{i+1}: 'length' должно быть положительным числом")
            if "quantity" not in stock or not isinstance(stock["quantity"], int) or stock["quantity"] <= 0:
                raise HTTPException(status_code=400, detail=f"Заготовка #{i+1}: 'quantity' должно быть положительным целым числом")
        
        # Валидация отрезков
        for i, cut in enumerate(cuts):
            if not isinstance(cut, dict):
                raise HTTPException(status_code=400, detail=f"Отрезок #{i+1} должен быть объектом")
            if "length" not in cut or not isinstance(cut["length"], (int, float)) or cut["length"] <= 0:
                raise HTTPException(status_code=400, detail=f"Отрезок #{i+1}: 'length' должно быть положительным числом")
            if "quantity" not in cut or not isinstance(cut["quantity"], int) or cut["quantity"] <= 0:
                raise HTTPException(status_code=400, detail=f"Отрезок #{i+1}: 'quantity' должно быть положительным целым числом")
        
        total_stocks_qty = sum(s.get("quantity", 1) for s in stocks)
        total_cuts_qty = sum(c.get("quantity", 1) for c in cuts)
        logger.info(f"Получен запрос на оптимизацию: {len(stocks)} типов заготовок (всего {total_stocks_qty} шт), {len(cuts)} типов отрезков (всего {total_cuts_qty} шт)")
        
        # Вызов алгоритма оптимизации
        import time
        start_time = time.time()
        result = optimize_cut(
            stocks=stocks,
            cuts=cuts,
            settings=settings
        )
        elapsed_time = time.time() - start_time
        
        logger.info(f"Оптимизация завершена успешно за {elapsed_time:.2f} секунд")
        return result
        
    except HTTPException:
        # Пробрасываем HTTP исключения как есть
        raise
    except Exception as e:
        # Логируем все остальные ошибки
        error_trace = traceback.format_exc()
        logger.error(f"Ошибка при выполнении оптимизации: {str(e)}\n{error_trace}")
        raise HTTPException(
            status_code=500,
            detail=f"Внутренняя ошибка сервера: {str(e)}"
        )


