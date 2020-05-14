from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired
from extensions import get_sort_list


class PoiSort(FlaskForm):
    start_sort = SelectField(validators=[DataRequired('Please choose')], default=1,
                             render_kw={
                                 "id": "start_sort",
                                 "onchange": "Select('start_sort', '#start_name', '/choose_name')"
                            })
    destination_sort = SelectField(validators=[DataRequired('Please choose')],
                                   default=1,
                                   render_kw={
                                       "id": "destination_sort",
                                       "onchange": "Select('destination_sort', '#destination_name', '/choose_name')"
                                   })
    start_name = SelectField(validators=[DataRequired('Please choose')], choices=(["---- Choose the name ----"]),
                             render_kw={
                                "id": "start_name"
                             })
    destination_name = SelectField(validators=[DataRequired('Please choose')], choices=(["---- Choose the name ----"]),
                                   render_kw={
                                       "id": "destination_name"
                                   })
    submit = SubmitField('submit')

    def __init__(self, *args, **kwargs):
        super(PoiSort, self).__init__(*args, **kwargs)
        self.start_sort.choices = get_sort_list()
        self.destination_sort.choices = get_sort_list()
