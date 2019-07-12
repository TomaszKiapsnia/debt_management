from flask import render_template, url_for, flash, redirect, request, Blueprint
from kanguru import app, db
from flask_login import login_required
from kanguru.interactions.forms import InteractionForm
from sqlalchemy.sql import func
from kanguru.models import Customer, Interaction

bp_interactions = Blueprint('interactions', __name__)

rows_per_page = 20


def calc_debt(customer_id):
    bill = db.session.query(func.coalesce(func.sum(Interaction.bill), 0)).filter(Interaction.customer_id == customer_id).first()
    paid = db.session.query(func.coalesce(func.sum(Interaction.paid), 0)).filter(Interaction.customer_id == customer_id).first()

    try:
        debt = paid[0] - bill[0]
    except:
        debt = 0

    return debt


@bp_interactions.route("/interactions/<int:interaction_id>/update", methods=['GET', 'POST'])
@login_required
def update_interaction(interaction_id):
    interaction = Interaction.query.get_or_404(interaction_id)
    form = InteractionForm()
    if form.validate_on_submit():
        interaction.details = form.details.data
        interaction.bill = form.bill.data
        interaction.paid = form.paid.data
        interaction.date = form.date.data
        db.session.commit()
        flash('Dane transakcji zmienione!', 'success')
        return redirect(url_for('interactions.customer_interactions', customer_id=interaction.customer_id))
    elif request.method == 'GET':
        form.details.data = interaction.details
        form.bill.data = interaction.bill
        form.paid.data = interaction.paid
        form.date.data = interaction.date
    return render_template('add_interaction.html', title='Zmiana transakcji',
                           form=form, legend='Update transakcji')


@bp_interactions.route("/interactions/<int:customer_id>")
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


@bp_interactions.route("/interactions/<int:customer_id>/new", methods=['GET', 'POST'])
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
        return redirect(url_for('interactions.customer_interactions', customer_id=customer.id))
    return render_template('add_interaction.html', title='Nowa transakcja',
                           form=form, legend='Nowa transakcja')


@bp_interactions.route("/interactions/<int:interaction_id>/delete", methods=['GET', 'POST'])
@login_required
def delete_interaction(interaction_id):
    interaction = Interaction.query.get_or_404(interaction_id)
    db.session.delete(interaction)
    db.session.commit()
    flash('Interakcja usunieta!', 'success')
    return redirect(url_for('interactions.customer_interactions', customer_id=interaction.customer_id))


@bp_interactions.route("/interactions/all_interactions_by_date")
@login_required
def all_interactions_by_date():
    page = request.args.get('page', 1, type=int)
    interactions = db.session.query(Interaction.id, Customer.details.label("customer_details"), Interaction.details, Interaction.bill, Interaction.paid, Interaction.date)\
        .outerjoin(Customer, Interaction.customer_id == Customer.id)\
        .order_by(Interaction.date.desc())\
        .paginate(page=1, per_page=rows_per_page)

    return render_template('all_interactions_by_date.html',
                           title='Wszystkie transakcje',
                           interactions=interactions)
