from flask import render_template, url_for, flash, redirect, request, Blueprint
from kanguru import app, db
from flask_login import login_required
from kanguru.interactions.forms import InteractionForm
from kanguru.models import Customer, Interaction

bp_interactions = Blueprint('interactions', __name__)


@bp_interactions.route("/interaction/<int:interaction_id>/update", methods=['GET', 'POST'])
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
        return redirect(url_for('customers.customer_interactions', customer_id=interaction.customer_id))
    elif request.method == 'GET':
        form.details.data = interaction.details
        form.bill.data = interaction.bill
        form.paid.data = interaction.paid
        form.date.data = interaction.date
    return render_template('add_interaction.html', title='Zmiana transakcji',
                           form=form, legend='Update transakcji')
