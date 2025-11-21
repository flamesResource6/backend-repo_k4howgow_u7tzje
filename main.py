import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import Product

app = FastAPI(title="Ecommerce API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def serialize_product(doc: dict) -> dict:
    if not doc:
        return {}
    d = doc.copy()
    if "_id" in d:
        d["id"] = str(d.pop("_id"))
    return d


MOCK_PRODUCTS = [
    {
        "title": "Minimalist Ceramic Mug",
        "description": "Matte white ceramic mug with ergonomic handle.",
        "price": 18.0,
        "category": "Home",
        "in_stock": True,
        "image": "https://images.unsplash.com/photo-1512496015851-a90fb38ba796?q=80&w=1200&auto=format&fit=crop"
    },
    {
        "title": "Wireless Over-Ear Headphones",
        "description": "Clean design, active noise cancellation, 30h battery.",
        "price": 199.0,
        "category": "Tech",
        "in_stock": True,
        "image": "https://images.unsplash.com/photo-1518443895914-6d27f6a58a15?q=80&w=1200&auto=format&fit=crop"
    },
    {
        "title": "Soft Cotton T-Shirt",
        "description": "Premium 220gsm cotton, relaxed fit, off-white.",
        "price": 28.0,
        "category": "Apparel",
        "in_stock": True,
        "image": "https://images.unsplash.com/photo-1520975682031-a700cf9f3160?q=80&w=1200&auto=format&fit=crop"
    },
    {
        "title": "Hardcover Dot Grid Notebook",
        "description": "A5 size, 160 pages, lays flat, recycled paper.",
        "price": 22.0,
        "category": "Office",
        "in_stock": True,
        "image": "https://images.unsplash.com/photo-1531346680769-9d39828e36a5?q=80&w=1200&auto=format&fit=crop"
    },
    {
        "title": "Minimal Desk Lamp",
        "description": "Adjustable warm LEDs with touch dimming.",
        "price": 79.0,
        "category": "Home",
        "in_stock": True,
        "image": "https://images.unsplash.com/photo-1493663284031-b7e3aefcae8e?q=80&w=1200&auto=format&fit=crop"
    },
    {
        "title": "Leather Wallet",
        "description": "Hand-stitched full-grain leather wallet with RFID blocking.",
        "price": 49.0,
        "category": "Accessories",
        "in_stock": True,
        "image": "https://images.unsplash.com/photo-1545289414-1c3cb1c06238?q=80&w=1200&auto=format&fit=crop"
    },
    {
        "title": "Insulated Water Bottle",
        "description": "Keeps drinks cold for 24h, hot for 12h, powder-coated finish.",
        "price": 32.0,
        "category": "Outdoors",
        "in_stock": True,
        "image": "https://images.unsplash.com/photo-1595433707802-6b2626ef1c86?q=80&w=1200&auto=format&fit=crop"
    },
    {
        "title": "Portable Bluetooth Speaker",
        "description": "Room-filling sound in a compact, splash-proof design.",
        "price": 89.0,
        "category": "Tech",
        "in_stock": True,
        "image": "https://images.unsplash.com/photo-1519671482749-fd09be7ccebf?q=80&w=1200&auto=format&fit=crop"
    },
    {
        "title": "Aromatherapy Candle",
        "description": "Soy wax candle with sandalwood and citrus notes.",
        "price": 24.0,
        "category": "Home",
        "in_stock": True,
        "image": "https://images.unsplash.com/photo-1519681393784-d120267933ba?q=80&w=1200&auto=format&fit=crop"
    },
    {
        "title": "Canvas Tote Bag",
        "description": "Heavy-duty 16oz canvas with inner pocket and zipper.",
        "price": 35.0,
        "category": "Accessories",
        "in_stock": True,
        "image": "https://images.unsplash.com/photo-1618354691458-3f58f5c65b15?q=80&w=1200&auto=format&fit=crop"
    },
    {
        "title": "Succulent Planter Set",
        "description": "Set of 3 ceramic planters with drainage trays.",
        "price": 27.0,
        "category": "Home",
        "in_stock": True,
        "image": "https://images.unsplash.com/photo-1501004318641-b39e6451bec6?q=80&w=1200&auto=format&fit=crop"
    },
    {
        "title": "Stainless Chef Knife",
        "description": "8-inch chef knife with balanced weight and ergonomic grip.",
        "price": 59.0,
        "category": "Kitchen",
        "in_stock": True,
        "image": "https://images.unsplash.com/photo-1594387102886-0b0a9f62d7db?q=80&w=1200&auto=format&fit=crop"
    }
]


@app.on_event("startup")
def startup_seed():
    try:
        if db is None:
            return
        count = db["product"].count_documents({})
        if count and count > 0:
            return
        for p in MOCK_PRODUCTS:
            create_document("product", p)
    except Exception:
        pass


@app.get("/")
def read_root():
    return {"message": "Ecommerce Backend Running"}


@app.get("/api/hello")
def hello():
    return {"message": "Hello from the backend API!"}


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"

            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"

    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    import os as _os
    response["database_url"] = "✅ Set" if _os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if _os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response


# -------------------- Ecommerce Endpoints --------------------
@app.get("/api/products")
def list_products(category: Optional[str] = None, limit: int = 24):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not available")
    filt = {"in_stock": True}
    if category:
        filt["category"] = category
    docs = get_documents("product", filt, limit)
    return [serialize_product(d) for d in docs]


@app.get("/api/products/{product_id}")
def get_product(product_id: str):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not available")
    try:
        oid = ObjectId(product_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid product id")

    doc = db["product"].find_one({"_id": oid})
    if not doc:
        raise HTTPException(status_code=404, detail="Product not found")
    return serialize_product(doc)


@app.post("/api/products", status_code=201)
def create_product(product: Product):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not available")
    new_id = create_document("product", product)
    doc = db["product"].find_one({"_id": ObjectId(new_id)})
    return serialize_product(doc)


@app.post("/api/seed")
def seed_products():
    if db is None:
        raise HTTPException(status_code=500, detail="Database not available")

    existing = db["product"].count_documents({})
    if existing > 0:
        return {"seeded": False, "message": "Products already exist"}

    inserted_ids = []
    for p in MOCK_PRODUCTS:
        inserted_ids.append(create_document("product", p))

    products = [serialize_product(db["product"].find_one({"_id": ObjectId(_id)})) for _id in inserted_ids]
    return {"seeded": True, "count": len(products), "products": products}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
