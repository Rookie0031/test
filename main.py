from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from concurrent.futures import ThreadPoolExecutor
import time

# FastAPI 인스턴스 생성
app = FastAPI()

# 데이터 모델 정의
class Item(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    price: float

# 메모리에 데이터 저장을 위한 임시 데이터베이스
items_db = []
# 스레드 풀 생성
thread_pool = ThreadPoolExecutor(max_workers=5)

# 메모리 누수 시뮬레이션을 위한 전역 변수
memory_leak_storage = []

@app.get("/")
async def read_root():
    return {"message": "안녕하세요! FastAPI 서버입니다."}
# GET 요청 처리 (모든 아이템 조회)
@app.get("/items/", response_model=List[Item])
async def read_items():
    return items_db

# GET 요청 처리 (특정 아이템 조회)
@app.get("/items/{item_id}", response_model=Item)
async def read_item(item_id: int):
    item = next((item for item in items_db if item.id == item_id), None)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

# POST 요청 처리 (새 아이템 생성)
@app.post("/items/", response_model=Item)
async def create_item(item: Item):
    if any(x.id == item.id for x in items_db):
        raise HTTPException(status_code=400, detail="Item ID already exists")
    items_db.append(item)
    return item

# PUT 요청 처리 (아이템 수정)
@app.put("/items/{item_id}", response_model=Item)
async def update_item(item_id: int, item: Item):
    item_idx = next((idx for idx, x in enumerate(items_db) if x.id == item_id), None)
    if item_idx is None:
        raise HTTPException(status_code=404, detail="Item not found")
    items_db[item_idx] = item
    return item

# DELETE 요청 처리 (아이템 삭제)
@app.delete("/items/{item_id}")
async def delete_item(item_id: int):
    item_idx = next((idx for idx, x in enumerate(items_db) if x.id == item_id), None)
    if item_idx is None:
        raise HTTPException(status_code=404, detail="Item not found")
    items_db.pop(item_idx)
    return {"message": "Item deleted successfully"}

# 멀티스레드 연산 처리 API
@app.get("/thread-tasks")
async def run_thread_tasks():
    start_time = time.time()
    
    # 스레드 풀을 사용하여 작업 실행
    tasks = [thread_pool.submit(cpu_bound_work, i) for i in range(5)]
    results = [task.result() for task in tasks]
    
    end_time = time.time()
    
    return {
        "results": results,
        "total_time": f"{end_time - start_time:.2f}초"
    }

# 일반 연산 처리 API
@app.get("/normal-tasks")
async def run_normal_tasks():
    start_time = time.time()
    
    # 순차적으로 작업 실행
    results = [cpu_bound_work(i) for i in range(5)]
    
    end_time = time.time()
    
    return {
        "results": results,
        "total_time": f"{end_time - start_time:.2f}초"
    }

# 메모리 누수 시뮬레이션 API
@app.get("/memory-leak")
async def simulate_memory_leak():
    # 더 큰 데이터를 생성하여 메모리에 저장
    # 약 100MB씩 증가 (이전보다 약 10배 증가)
    data = ["*" * 1024 * 1024 * 100] * 1  # 한번에 약 100MB
    memory_leak_storage.extend(data)
    
    current_size_mb = len(memory_leak_storage) * 100  # 대략적인 크기 (MB)
    
    return {
        "message": "메모리 누수 시뮬레이션 실행됨",
        "stored_items": len(memory_leak_storage),
        "approximate_size_mb": f"{current_size_mb}MB"
    }

# CPU 집약적 작업 시뮬레이션 API
@app.get("/cpu-intensive")
async def cpu_intensive_task():
    start_time = time.time()
    
    # CPU를 intensive하게 사용하는 작업 (더 가벼운 버전)
    result = 0
    for i in range(10**6):  # 10만번으로 줄임
        # 비효율적인 소수 판별
        if i > 1:
            is_prime = True
            for j in range(2, int(i ** 0.5) + 1):
                if i % j == 0:
                    is_prime = False
                    break
            if is_prime:
                result += i
        
        # 간단한 수학 연산 추가
        result += (i ** 2) % 1000
    
    end_time = time.time()
    
    return {
        "message": "CPU 집약적 작업 완료",
        "execution_time": f"{end_time - start_time:.2f}초",
        "result": result
    }

# Other functions
# CPU 바운드 작업을 시뮬레이션하는 함수
def cpu_bound_work(task_id: int) -> dict:
    time.sleep(1)  # 복잡한 연산 시뮬레이션
    return {"task_id": task_id, "result": f"작업 {task_id} 완료"}