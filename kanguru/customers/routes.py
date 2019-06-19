from flask import render_template, url_for, flash, redirect, request, Blueprint
from kanguru import db, bcrypt
from flask_login import login_user, current_user, logout_user, login_required
from kanguru.customers.forms import LoginForm, CustomerForm, SearchForm
from kanguru.interactions.forms import InteractionForm
from kanguru.models import Customer, Interaction, Employee
from sqlalchemy.sql import func
from datetime import datetime, timedelta


bp_customers = Blueprint('customers', __name__)

rows_per_page = 2


@bp_customers.route("/", methods=['GET', 'POST'])
@bp_customers.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('customers.customers'))
    form = LoginForm()
    if form.validate_on_submit():
        employee = Employee.query.filter_by(username=form.username.data).first()
        if employee and bcrypt.check_password_hash(employee.password, form.password.data):
            login_user(employee, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('customers.customers'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@bp_customers.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('customers.login'))


@bp_customers.route("/customers", methods=['GET', 'POST'])
@login_required
def customers():
    form = SearchForm()
    page = request.args.get('page', 1, type=int)
    if form.details.data is not None:
        # customers = db.engine.execute("""SELECT c.id
        #                                             ,c.details
        #                                             ,COALESCE(SUM(i.paid-i.bill),0)
        #                                        FROM customer c
        #                                   LEFT JOIN interaction i
        #                                          ON c.id = i.customer_id
        #                                       WHERE c.details LIKE '%""" + str(form.details.data).replace("'", "").replace('"', '') + """%'
        #                                    GROUP BY c.id, c.details
        #                                    ORDER BY c.details ASC""")

        customers = db.session.query(Customer.id, Customer.details, func.coalesce(func.sum(Interaction.paid - Interaction.bill), 0).label('debt'))\
            .outerjoin(Interaction, Interaction.customer_id == Customer.id)\
            .filter(Customer.details.like('%' + form.details.data + '%'))\
            .group_by(Customer.details, Customer.id)\
            .order_by(Customer.details.desc())\
            .paginate(page=1, per_page=rows_per_page)
    else:

        customers = db.session.query(Customer.id, Customer.details, func.coalesce(func.sum(Interaction.paid - Interaction.bill), 0).label('debt'))\
            .outerjoin(Interaction, Interaction.customer_id == Customer.id)\
            .group_by(Customer.details, Customer.id)\
            .order_by(Customer.details.desc())\
            .paginate(page=page, per_page=rows_per_page)
        # customers = db.engine.execute("""SELECT c.id
        #                                        ,c.details
        #                                        ,COALESCE(SUM(i.paid-i.bill),0) AS debt
        #                                    FROM customer c
        #                               LEFT JOIN interaction i
        #                                      ON c.id = i.customer_id
        #                                GROUP BY c.id, c.details
        #                                ORDER BY c.details ASC""")

    return render_template('customers.html', title='Klient', customers=customers, form=form)


def calc_debt(customer_id):
    bill = db.session.query(func.coalesce(func.sum(Interaction.bill), 0)).filter(Interaction.customer_id == customer_id).first()
    paid = db.session.query(func.coalesce(func.sum(Interaction.paid), 0)).filter(Interaction.customer_id == customer_id).first()

    try:
        debt = paid[0] - bill[0]
    except:
        debt = 0

    return debt


@bp_customers.route("/add_customer", methods=['GET', 'POST'])
@login_required
def add_customer():
    form = CustomerForm()
    if form.validate_on_submit():
        new_customer = Customer(details=form.details.data)
        db.session.add(new_customer)
        db.session.commit()
        return redirect(url_for('customers.customers'))
    return render_template('add_customer.html', title='Dodaj klienta', form=form, legend='Dodaj klienta')


@bp_customers.route("/customer/<int:customer_id>")
def customer(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    debt = calc_debt(customer_id)

    lm_year = (datetime.now() - timedelta(days=datetime.now().day + 1)).year
    lm_month = (datetime.now() - timedelta(days=datetime.now().day + 1)).month

    lm_bill = db.session.query(func.coalesce(func.sum(Interaction.bill), 0)).filter(Interaction.customer_id == customer_id).filter(func.extract('year', Interaction.date) == lm_year).filter(func.extract('month', Interaction.date) == lm_month).first()
    lm_paid = db.session.query(func.coalesce(func.sum(Interaction.paid), 0)).filter(Interaction.customer_id == customer_id).filter(func.extract('year', Interaction.date) == lm_year).filter(func.extract('month', Interaction.date) == lm_month).first()

    try:
        lm_debt = lm_paid[0] - lm_bill[0]
    except:
        lm_debt = 0

    return render_template('customer.html', title=customer.details, customer=customer, debt=debt, lm_month=lm_month, lm_year=lm_year, lm_debt=lm_debt, lm_bill=lm_bill[0])


@bp_customers.route("/customer/<int:customer_id>/update", methods=['GET', 'POST'])
@login_required
def update_customer(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    form = CustomerForm()
    if form.validate_on_submit():
        customer.details = form.details.data
        db.session.commit()
        flash('Dane klienta zmienione!', 'success')
        return redirect(url_for('customers.customer', customer_id=customer.id))
    elif request.method == 'GET':
        form.details.data = customer.details
    return render_template('add_customer.html', title='Zmiana danych klienta',
                           form=form, legend='Update klienta')


@bp_customers.route("/customer/<int:customer_id>/delete", methods=['POST'])
@login_required
def delete_customer(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    db.session.delete(customer)
    db.session.commit()
    flash('Klient usuniety!', 'success')
    return redirect(url_for('customers.customers'))


@bp_customers.route("/customer/<int:customer_id>/interactions")
@login_required
def customer_interactions(customer_id):
    page = request.args.get('page', 1, type=int)
    customer_interactions = Interaction.query.filter_by(customer_id=customer_id)\
        .order_by(Interaction.date.desc())\
        .paginate(page=page, per_page=rows_per_page)
    customer = Customer.query.get_or_404(customer_id)
    debt = calc_debt(customer_id)
    return render_template('customer_interactions.html',
                           title='Transakcje klienta',
                           interactions=customer_interactions,
                           customer=customer,
                           debt=debt)


@bp_customers.route("/customer/<int:customer_id>/add_interaction", methods=['GET', 'POST'])
@login_required
def add_interaction(customer_id):
    form = InteractionForm()
    customer = Customer.query.get_or_404(customer_id)
    if form.validate_on_submit():
        new_interaction = Interaction(details=form.details.data,
                                      customer_id=customer_id,
                                      date=form.date.data,
                                      bill=form.bill.data,
                                      paid=form.paid.data)
        db.session.add(new_interaction)
        db.session.commit()
        return redirect(url_for('customers.customer_interactions', customer_id=customer.id))
    return render_template('add_interaction.html', title='Nowa transakcja',
                           form=form, legend='Nowa transakcja')
