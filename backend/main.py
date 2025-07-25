from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from db import get_connection

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # for dev; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/get-names")
def get_names():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT subroad FROM bengaluru ORDER BY subroad;")
    names = [row[0] for row in cur.fetchall()]
    conn.close()
    return names



@app.get("/get-points")
def get_points(name: str):
    conn = get_connection()
    cur = conn.cursor()
    print(f"Fetching points for district: {name}")  # Debug print
    try:
        cur.execute("""
            SELECT jsonb_build_object(
                'type', 'FeatureCollection',
                'features', jsonb_agg(ST_AsGeoJSON(p.*)::jsonb)
            )
            FROM points p
            JOIN district_boundary poly ON poly.name = %s
            WHERE ST_Within(p.geom, poly.geom);
        """, (name,))
        result = cur.fetchone()[0]
        print("Result:", result)  # Debug print

        if result is None:
            return {"error": f"No data found for district: {name}"}
        return result
    except Exception as e:
        return {"error": str(e)}
    finally:
        conn.close()

