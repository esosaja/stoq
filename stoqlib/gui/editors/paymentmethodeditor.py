# -*- coding: utf-8 -*-
# vi:si:et:sw=4:sts=4:ts=4

##
## Copyright (C) 2006-2011 Async Open Source <http://www.async.com.br>
## All rights reserved
##
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU Lesser General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU Lesser General Public License for more details.
##
## You should have received a copy of the GNU Lesser General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., or visit: http://www.gnu.org/.
##
## Author(s): Stoq Team <stoq-devel@async.com.br>
##
""" Editors for payment method management.  """


from kiwi.datatypes import ValidationError

from stoqlib.api import api
from stoqlib.domain.account import Account
from stoqlib.domain.payment.method import PaymentMethod
from stoqlib.gui.base.dialogs import run_dialog
from stoqlib.gui.editors.baseeditor import BaseEditor
from stoqlib.lib.translation import stoqlib_gettext


_ = stoqlib_gettext


class PaymentMethodEditor(BaseEditor):
    model_name = _('Payment Method')
    gladefile = 'PaymentMethodEditor'
    proxy_widgets = ('account',
                     'max_installments',
                     'penalty',
                     'daily_interest')

    def __init__(self, store, model):
        """
        Create a new PaymentMethodEditor object.
        :param store: a store
        :param model: an adapter of PaymentMethod which means a subclass of
                      PaymentMethod
        """
        self.model_type = PaymentMethod
        BaseEditor.__init__(self, store, model)
        self.set_description(model.description)

    def _setup_widgets(self):
        accounts = Account.select(store=self.store)
        self.account.prefill(api.for_combo(
            accounts, attr='long_description'))
        self.account.select(self.model.destination_account)

    #
    # BaseEditor Hooks
    #

    def setup_proxies(self):
        self._setup_widgets()
        self.add_proxy(self.model, PaymentMethodEditor.proxy_widgets)

    def on_confirm(self):
        self.model.destination_account = self.account.get_selected()

    #
    #   Validators
    #

    def on_daily_interest__validate(self, widget, value):
        if value < 0:
            return ValidationError(_(u'The value must be positive.'))

    def on_penalty__validate(self, widget, value):
        if value < 0:
            return ValidationError(_(u'The value must be positive.'))

    def on_max_installments__validate(self, widget, value):
        if value <= 0:
            return ValidationError(_(u'The value must be positive.'))


class CardPaymentMethodEditor(PaymentMethodEditor):

    def __init__(self, store, model):
        PaymentMethodEditor.__init__(self, store, model)
        button = self.add_button(_(u'Edit providers'))
        button.connect('clicked', self._on_edit_buton_clicked)

    def _on_edit_buton_clicked(self, button):
        # This will change in the next commit
        pass


def test():  # pragma nocover
    creator = api.prepare_test()
    money = PaymentMethod.get_by_name(creator.store, 'bill')
    retval = run_dialog(PaymentMethodEditor, None, creator.store, money)
    creator.store.confirm(retval)


if __name__ == '__main__':  # pragma nocover
    test()
