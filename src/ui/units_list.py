from kivy.adapters.listadapter import ListAdapter
from kivy.uix.listview import ListItemButton, ListView


args_converter = lambda row_index, rec: {'text': rec,
                                         'size_hint_y': 0.1,
                                         'height': 25}


def create_units_list(units, on_unit_selected):
    list_adapter = ListAdapter(data=units,
                               args_converter=args_converter,
                               cls=ListItemButton,
                               selection_mode='single',
                               allow_empty_selection=False)

    list_adapter.bind(on_selection_change=on_unit_selected)

    return ListView(adapter=list_adapter, size_hint_x=None, width=100)
