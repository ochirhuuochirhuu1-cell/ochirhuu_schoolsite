from flask import Flask, render_template, request, redirect, url_for, flash, session, abort
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import sqlite3
import os
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "database.db"

app = Flask(__name__)
# Үйлдвэрлэлийн орчинд SECRET_KEY-г environment variable-аас тохируулна.
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "replace-this-secret-key-before-deployment")
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

# Эхний хувилбарын жишээ хөтөлбөрүүд. Өөрийн сургуулийн баталгаатай нэрээр солино.
PROGRAMS = [
    {"slug": "software-development", "name": "Программ хангамжийн хөгжүүлэлт", "short": "Программчлал, веб болон программ хангамж хөгжүүлэх суурь мэдлэг, ур чадвар.", "duration": "3 жил", "icon": "💻"},
    {"slug": "information-technology", "name": "Мэдээллийн технологи", "short": "Компьютер, сүлжээ, мэдээллийн систем болон дижитал технологийн чиглэл.", "duration": "3 жил", "icon": "🖥️"},
    {"slug": "electrical-equipment", "name": "Цахилгаан тоног төхөөрөмж", "short": "Цахилгаан тоног төхөөрөмжийн ашиглалт, угсралт, засвар үйлчилгээний чиглэл.", "duration": "3 жил", "icon": "⚡"},
    {"slug": "aircraft-mechanics", "name": "Нисэх техникийн механик", "short": "Нисэхийн техникийн тоног төхөөрөмжийн үзлэг, засвар үйлчилгээний суурь ур чадвар.", "duration": "3 жил", "icon": "✈️"},
    {"slug": "automotive", "name": "Автомашины засвар үйлчилгээ", "short": "Автомашины бүтэц, оношилгоо, засвар үйлчилгээний практик ур чадвар.", "duration": "3 жил", "icon": "🚗"},
    {"slug": "welding", "name": "Гагнуур", "short": "Гагнуурын технологи, тоног төхөөрөмжийн ашиглалт, үйлдвэрлэлийн дадлага.", "duration": "3 жил", "icon": "🔧"},
]

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            phone TEXT NOT NULL,
            email TEXT,
            program TEXT NOT NULL,
            school TEXT,
            note TEXT,
            created_at TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close() 


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "admin_id" not in session:
            return redirect(url_for("admin_login", next=request.path))
        return view(*args, **kwargs)
    return wrapped

@app.context_processor
def inject_globals():
    return {"programs": PROGRAMS}

@app.route("/")
def home():
    return render_template("index.html", title="Нүүр")

@app.route("/about")
def about():
    return render_template("about.html", title="Бидний тухай")

@app.route("/programs")
def programs_page():
    return render_template("programs.html", title="Хөтөлбөрүүд")

@app.route("/program/<slug>")
def program_detail(slug):
    program = next((p for p in PROGRAMS if p["slug"] == slug), None)
    if not program:
        abort(404)
    return render_template("program_detail.html", title=program["name"], program=program)

@app.route("/admission", methods=["GET", "POST"])
def admission():
    selected_program = request.args.get("program", "")
    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        phone = request.form.get("phone", "").strip()
        email = request.form.get("email", "").strip()
        program = request.form.get("program", "").strip()
        school = request.form.get("school", "").strip()
        note = request.form.get("note", "").strip()

        allowed_programs = {p["name"] for p in PROGRAMS}
        if not full_name or not phone or program not in allowed_programs:
            flash("Овог нэр, утасны дугаар, зөв мэргэжлээ заавал бөглөнө үү.", "error")
            return render_template("admission.html", title="Элсэлтийн бүртгэл", selected_program=program)

        conn = get_db()
        conn.execute("""INSERT INTO applications
            (full_name, phone, email, program, school, note, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (full_name, phone, email, program, school, note, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        conn.close()
        flash("Таны бүртгэл амжилттай хадгалагдлаа. Сургууль тантай холбогдоно.", "success")
        return redirect(url_for("admission"))
    return render_template("admission.html", title="Элсэлтийн бүртгэл", selected_program=selected_program)

@app.route("/news")
def news():
    news_items = [
        {"date": "2026.10.20", "title": "Их Засаг Политехник Коллежийн шинэ элсэлтийн мэдээлэл", "text": "Шинэ хичээлийн жилийн элсэлтийн бүртгэл эхэллээ."},
        {"date": "2026.10.15", "title": "Оюутнуудын мэргэжлийн дадлага", "text": "Мэргэжлийн хөтөлбөрийн хүрээнд практик сургалт, дадлага зохион байгуулагдлаа."},
        {"date": "2026.10.10", "title": "Сургалтын орчин, лабораторийн шинэчлэл", "text": "Сургалтын орчныг шинэчилж, дадлагын тоног төхөөрөмжийг нэмэгдүүлж байна."}
    ]
    return render_template("news.html", title="Мэдээ мэдээлэл", news_items=news_items)

@app.route("/contact")
def contact():
    return render_template("contact.html", title="Холбоо барих")

# Анхны админ үүсгэх: командын мөрөөс `flask --app app create-admin` ажиллуулна.
@app.cli.command("create-admin")
def create_admin():
    """Админы хэрэглэгч үүсгэнэ. Нууц үгийг терминал дээр нууж асууна."""
    import getpass
    init_db()
    username = input("Админ хэрэглэгчийн нэр: ").strip()
    password = getpass.getpass("Шинэ нууц үг (дор хаяж 12 тэмдэгт): ")
    confirm = getpass.getpass("Нууц үгээ давтан оруулна уу: ")
    if len(password) < 12:
        print("Алдаа: нууц үг дор хаяж 12 тэмдэгт байх ёстой.")
        return
    if password != confirm:
        print("Алдаа: нууц үг таарахгүй байна.")
        return
    if not username:
        print("Алдаа: хэрэглэгчийн нэр хоосон байна.")
        return
    conn = get_db()
    try:
        conn.execute("INSERT INTO admins (username, password_hash, created_at) VALUES (?, ?, ?)",
                     (username, generate_password_hash(password), datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        print("Админ амжилттай үүслээ. /admin/login хаягаар нэвтэрнэ үү.")
    except sqlite3.IntegrityError:
        print("Энэ хэрэглэгчийн нэр аль хэдийн бүртгэлтэй байна.")
    finally:
        conn.close()

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if "admin_id" in session:
        return redirect(url_for("admin_dashboard"))
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        conn = get_db()
        admin = conn.execute("SELECT * FROM admins WHERE username = ?", (username,)).fetchone()
        conn.close()
        if admin and check_password_hash(admin["password_hash"], password):
            session.clear()
            session["admin_id"] = admin["id"]
            session["admin_username"] = admin["username"]
            flash("Амжилттай нэвтэрлээ.", "success")
            return redirect(url_for("admin_dashboard"))
        flash("Хэрэглэгчийн нэр эсвэл нууц үг буруу байна.", "error")
    return render_template("admin/login.html", title="Админ нэвтрэх")

@app.post("/admin/logout")
@admin_required
def admin_logout():
    session.clear()
    flash("Та системээс гарлаа.", "success")
    return redirect(url_for("admin_login"))

@app.route("/admin")
@app.route("/admin/applications")
@admin_required
def admin_dashboard():
    q = request.args.get("q", "").strip()
    conn = get_db()
    total = conn.execute("SELECT COUNT(*) AS n FROM applications").fetchone()["n"]
    if q:
        like = f"%{q}%"
        rows = conn.execute("""
            SELECT * FROM applications
            WHERE full_name LIKE ? OR phone LIKE ? OR email LIKE ? OR program LIKE ?
            ORDER BY id DESC
        """, (like, like, like, like)).fetchall()
    else:
        rows = conn.execute("SELECT * FROM applications ORDER BY id DESC").fetchall()
    conn.close()
    return render_template("admin/dashboard.html", title="Бүртгүүлэгчид", applications=rows, q=q, total=total)

@app.post("/admin/applications/<int:application_id>/delete")
@admin_required
def delete_application(application_id):
    # POST хүсэлт ашиглаж санамсаргүй устгалын эрсдэлийг бууруулна.
    conn = get_db()
    row = conn.execute("SELECT id FROM applications WHERE id = ?", (application_id,)).fetchone()
    if row:
        conn.execute("DELETE FROM applications WHERE id = ?", (application_id,))
        conn.commit()
        flash(f"#{application_id} бүртгэлийг устгалаа.", "success")
    else:
        flash("Бүртгэл олдсонгүй.", "error")
    conn.close()
    return redirect(url_for("admin_dashboard", q=request.form.get("q", "")))

if __name__ == "__main__":
    init_db()
    app.run(debug=True, host="127.0.0.1", port=5000)
