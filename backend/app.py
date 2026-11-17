from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from pathlib import Path
import joblib
import pandas as pd

# =========================================================
# PATHS
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATABASE_DIR = BASE_DIR / "database"
MODEL_DIR = BASE_DIR / "model"

DATABASE_DIR.mkdir(exist_ok=True)
MODEL_DIR.mkdir(exist_ok=True)


# =========================================================
# FLASK CONFIGURATION
# =========================================================

app = Flask(__name__)

app.secret_key = "assured-farming-secret-key"

app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"sqlite:///{DATABASE_DIR / 'assured_farming.db'}"
)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# =========================================================
# LOAD ML MODEL
# =========================================================

MODEL_PATH = MODEL_DIR / "random_forest_price_model.pkl"

model = None

try:
    model = joblib.load(MODEL_PATH)
    print("Random Forest model loaded successfully!")
except Exception as e:
    print("WARNING: Random Forest model could not be loaded.")
    print(e)


# =========================================================
# DATABASE MODELS
# =========================================================

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(
        db.String(100),
        nullable=False
    )

    email = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    password = db.Column(
        db.String(255),
        nullable=False
    )

    role = db.Column(
        db.String(20),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )


class Contract(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    buyer_name = db.Column(
        db.String(100),
        nullable=False
    )

    crop = db.Column(
        db.String(100),
        nullable=False
    )

    quantity = db.Column(
        db.String(100),
        nullable=False
    )

    price = db.Column(
        db.Float,
        nullable=False
    )

    quality = db.Column(
        db.String(100),
        nullable=False
    )

    delivery_location = db.Column(
        db.String(200),
        nullable=False
    )

    status = db.Column(
        db.String(30),
        default="Available"
    )


class Application(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    farmer_id = db.Column(
        db.Integer,
        nullable=False
    )

    contract_id = db.Column(
        db.Integer,
        nullable=False
    )

    status = db.Column(
        db.String(30),
        default="Pending"
    )


# =========================================================
# CREATE DATABASE
# =========================================================

with app.app_context():

    db.create_all()

    print("Database created successfully!")


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def farmer_required():

    if "user_id" not in session:
        return redirect("/login")

    if session.get("role") != "farmer":
        return "Access denied"

    return None


def buyer_required():

    if "user_id" not in session:
        return redirect("/login")

    if session.get("role") != "buyer":
        return "Access denied"

    return None


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():

    return render_template("index.html")


# =========================================================
# REGISTER
# =========================================================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        role = request.form.get("role")

        if not name or not email or not password or not role:
            return "Please fill all fields."

        existing_user = User.query.filter_by(
            email=email
        ).first()

        if existing_user:
            return "Email already registered."

        new_user = User(
            name=name,
            email=email,
            password=password,
            role=role
        )

        db.session.add(new_user)
        db.session.commit()

        return redirect("/login")

    return render_template("register.html")


# =========================================================
# LOGIN
# =========================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(
            email=email,
            password=password
        ).first()

        if not user:
            return "Invalid email or password."

        session["user_id"] = user.id
        session["user_name"] = user.name
        session["role"] = user.role

        if user.role == "farmer":
            return redirect("/farmer-dashboard")

        if user.role == "buyer":
            return redirect("/buyer-dashboard")

        return "Invalid user role."

    return render_template("login.html")


# =========================================================
# LOGOUT
# =========================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")


# =========================================================
# FARMER DASHBOARD
# =========================================================

@app.route("/farmer-dashboard")
def farmer_dashboard():

    check = farmer_required()

    if check:
        return check

    user = User.query.get(session["user_id"])

    return render_template(
        "farmer_dashboard.html",
        user=user
    )


# =========================================================
# BUYER DASHBOARD
# =========================================================

@app.route("/buyer-dashboard")
def buyer_dashboard():

    check = buyer_required()

    if check:
        return check

    user = User.query.get(session["user_id"])

    contract_count = Contract.query.filter_by(
        buyer_name=session["user_name"]
    ).count()

    return render_template(
        "buyer_dashboard.html",
        user=user,
        contract_count=contract_count
    )


# =========================================================
# =========================================================
# FARMER - AVAILABLE CONTRACTS
# =========================================================
# =========================================================

@app.route("/contracts")
def contracts():

    check = farmer_required()

    if check:
        return check

    contracts = Contract.query.filter_by(
        status="Available"
    ).all()

    return render_template(
        "contract.html",
        contracts=contracts
    )


# =========================================================
# FARMER - APPLY FOR CONTRACT
# =========================================================

@app.route("/apply/<int:contract_id>")
def apply_contract(contract_id):

    check = farmer_required()

    if check:
        return check

    contract = Contract.query.get_or_404(
        contract_id
    )

    # Prevent duplicate application
    existing_application = Application.query.filter_by(
        farmer_id=session["user_id"],
        contract_id=contract_id
    ).first()

    if existing_application:

        return redirect("/applications")

    new_application = Application(
        farmer_id=session["user_id"],
        contract_id=contract_id,
        status="Pending"
    )

    db.session.add(new_application)
    db.session.commit()

    return redirect("/applications")


# =========================================================
# FARMER - MY APPLICATIONS
# =========================================================

@app.route("/applications")
def applications():

    check = farmer_required()

    if check:
        return check

    rows = (
        db.session.query(
            Application,
            Contract
        )
        .join(
            Contract,
            Application.contract_id == Contract.id
        )
        .filter(
            Application.farmer_id == session["user_id"]
        )
        .all()
    )

    return render_template(
        "applications.html",
        applications=rows
    )


# =========================================================
# PROFILE - BOTH FARMER AND BUYER
# =========================================================

@app.route("/profile")
def profile():

    if "user_id" not in session:
        return redirect("/login")

    user = User.query.get(session["user_id"])

    if user is None:
        session.clear()
        return redirect("/login")

    return render_template(
        "profile.html",
        user=user
    )

# =========================================================
# =========================================================
# BUYER - CREATE CONTRACT
# =========================================================
# =========================================================

@app.route("/create-contract", methods=["GET", "POST"])
def create_contract():

    check = buyer_required()

    if check:
        return check

    if request.method == "POST":

        buyer_name = session["user_name"]

        crop = request.form.get("crop", "").strip()
        quantity = request.form.get("quantity", "").strip()
        price_text = request.form.get("price", "").strip()
        quality = request.form.get("quality", "").strip()
        delivery_location = request.form.get(
            "delivery_location",
            ""
        ).strip()

        # Check empty fields
        if not crop or not quantity or not price_text:
            return "Please fill all required fields."

        if not quality or not delivery_location:
            return "Please fill all required fields."

        # Check price
        try:
            price = float(price_text)

        except ValueError:
            return "Price must be a valid number."

        if price <= 0:
            return "Price must be greater than zero."

        # -------------------------------------------------
        # DUPLICATE CONTRACT CHECK
        # -------------------------------------------------

        existing_contract = Contract.query.filter_by(
            buyer_name=buyer_name,
            crop=crop,
            quantity=quantity,
            price=price,
            quality=quality,
            delivery_location=delivery_location
        ).first()

        # If already exists, DO NOT create again
        if existing_contract:

            return redirect("/my-contracts")

        # -------------------------------------------------
        # CREATE ONLY ONCE
        # -------------------------------------------------

        new_contract = Contract(
            buyer_name=buyer_name,
            crop=crop,
            quantity=quantity,
            price=price,
            quality=quality,
            delivery_location=delivery_location,
            status="Available"
        )

        db.session.add(new_contract)
        db.session.commit()

        return redirect("/my-contracts")

    return render_template(
        "create_contract.html"
    )


# =========================================================
# BUYER - MY CONTRACTS
# =========================================================

@app.route("/my-contracts")
def my_contracts():

    check = buyer_required()

    if check:
        return check

    contracts = Contract.query.filter_by(
        buyer_name=session["user_name"]
    ).order_by(
        Contract.id.desc()
    ).all()

    return render_template(
        "my_contracts.html",
        contracts=contracts
    )


# =========================================================
# BUYER - APPLICATIONS
# =========================================================

@app.route("/buyer-applications")
def buyer_applications():

    check = buyer_required()

    if check:
        return check

    # IMPORTANT:
    # We send actual ORM objects instead of dictionaries.
    # Therefore Jinja can safely use:
    # application.id
    # application.status
    # contract.crop
    # farmer.name

    rows = (
        db.session.query(
            Application,
            Contract,
            User
        )
        .join(
            Contract,
            Application.contract_id == Contract.id
        )
        .join(
            User,
            Application.farmer_id == User.id
        )
        .filter(
            Contract.buyer_name == session["user_name"]
        )
        .order_by(
            Application.id.desc()
        )
        .all()
    )

    return render_template(
        "buyer_applications.html",
        applications=rows
    )


# =========================================================
# BUYER - ACCEPT / REJECT APPLICATION
# =========================================================

@app.route(
    "/buyer-application/<int:application_id>/<action>"
)
def update_application(
    application_id,
    action
):

    check = buyer_required()

    if check:
        return check

    application = Application.query.get_or_404(
        application_id
    )

    contract = Contract.query.get(
        application.contract_id
    )

    if not contract:
        return "Contract not found."

    # Make sure this buyer owns the contract
    if contract.buyer_name != session["user_name"]:
        return "Access denied"

    if action == "accept":

        application.status = "Accepted"

        contract.status = "Accepted"

        db.session.commit()

        return redirect("/buyer-applications")

    elif action == "reject":

        application.status = "Rejected"

        db.session.commit()

        return redirect("/buyer-applications")

    return "Invalid action."


# =========================================================
# PRICE PREDICTION
# =========================================================

@app.route("/predict", methods=["GET", "POST"])
def predict():

    check = farmer_required()

    if check:
        return check

    prediction = None
    error = None

    if request.method == "POST":

        try:

            input_data = pd.DataFrame([{

                "State":
                    request.form.get("state"),

                "District":
                    request.form.get("district"),

                "Market":
                    request.form.get("market"),

                "Commodity":
                    request.form.get("commodity"),

                "Variety":
                    request.form.get("variety"),

                "Grade":
                    request.form.get("grade"),

                "Min Price":
                    float(request.form.get("min_price")),

                "Max Price":
                    float(request.form.get("max_price")),

                "Year":
                    int(request.form.get("year")),

                "Month":
                    int(request.form.get("month")),

                "Day":
                    int(request.form.get("day")),

                "DayOfWeek":
                    int(request.form.get("day_of_week")),

                "Quarter":
                    int(request.form.get("quarter")),

                "Season":
                    request.form.get("season")
            }])

            if model is None:

                error = "Random Forest model is not loaded."

            else:

                prediction = model.predict(
                    input_data
                )[0]

                prediction = round(
                    float(prediction),
                    2
                )

        except Exception as e:

            error = f"Prediction error: {e}"

    return render_template(
        "predict_price.html",
        prediction=prediction,
        error=error
    )


# =========================================================
# ERROR HANDLERS
# =========================================================

@app.errorhandler(404)
def page_not_found(error):

    return """
    <h2>Page Not Found</h2>
    <p>The requested page does not exist.</p>
    <a href="/">Go to Home</a>
    """, 404


@app.errorhandler(500)
def internal_error(error):

    db.session.rollback()

    return """
    <h2>Something went wrong</h2>
    <p>Please go back and try again.</p>
    <a href="/">Go to Home</a>
    """, 500


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )