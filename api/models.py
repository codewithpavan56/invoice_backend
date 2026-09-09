from django.db import models

class User(models.Model):
    id = models.CharField(primary_key=True, max_length=100)
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    password_hash = models.CharField(max_length=255)
    fullName = models.CharField(max_length=255, db_column='fullName', blank=True, null=True)
    avatarUrl = models.TextField(db_column='avatarUrl', blank=True, null=True)
    notifications = models.TextField(blank=True, null=True) # JSON string
    visualPreference = models.CharField(max_length=50, db_column='visualPreference', default='light')

    class Meta:
        db_table = 'users'

class Client(models.Model):
    id = models.CharField(primary_key=True, max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column='user_id')
    email = models.EmailField()
    businessName = models.CharField(max_length=255, db_column='businessName')
    address = models.TextField(blank=True, null=True)
    extraInfo = models.TextField(db_column='extraInfo', blank=True, null=True)
    website = models.CharField(max_length=255, blank=True, null=True)
    firstName = models.CharField(max_length=100, db_column='firstName', blank=True, null=True)
    lastName = models.CharField(max_length=100, db_column='lastName', blank=True, null=True)
    gstNo = models.CharField(max_length=100, db_column='gst_no', blank=True, null=True)

    class Meta:
        db_table = 'clients'

class Invoice(models.Model):
    id = models.CharField(primary_key=True, max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column='user_id')
    invoiceNumber = models.CharField(max_length=100, db_column='invoiceNumber')
    orderNumber = models.CharField(max_length=100, db_column='orderNumber', blank=True, null=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, db_column='clientId')
    status = models.CharField(max_length=50)
    createdDate = models.CharField(max_length=100, db_column='createdDate')
    dueDate = models.CharField(max_length=100, db_column='dueDate')
    subTotal = models.FloatField(db_column='subTotal')
    discount = models.FloatField(default=0)
    taxRate = models.FloatField(default=0, db_column='taxRate')
    taxAmount = models.FloatField(default=0, db_column='taxAmount')
    paidAmount = models.FloatField(default=0, db_column='paidAmount')
    totalDue = models.FloatField(db_column='totalDue')
    terms = models.TextField(blank=True, null=True)
    footer = models.TextField(blank=True, null=True)
    title = models.CharField(max_length=255, blank=True, null=True)
    hsnCode = models.CharField(max_length=100, db_column='hsnCode', blank=True, null=True)
    quotationNumber = models.CharField(max_length=100, db_column='quotationNumber', blank=True, null=True)

    class Meta:
        db_table = 'invoices'

class InvoiceItem(models.Model):
    id = models.CharField(primary_key=True, max_length=100)
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, db_column='invoice_id', related_name='items')
    qty = models.FloatField()
    title = models.CharField(max_length=255)
    adjustPercent = models.FloatField(default=0, db_column='adjustPercent')
    rate = models.FloatField()
    amount = models.FloatField()
    description = models.TextField(blank=True, null=True)
    taxable = models.IntegerField(default=1) # SQLite integer mapping
    hsnCode = models.CharField(max_length=100, db_column='hsnCode', blank=True, null=True)

    class Meta:
        db_table = 'invoice_items'

class Payment(models.Model):
    id = models.CharField(primary_key=True, max_length=100)
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, db_column='invoice_id', related_name='payments')
    date = models.CharField(max_length=100)
    amount = models.FloatField()
    paymentMethod = models.CharField(max_length=100, db_column='paymentMethod')
    paymentId = models.CharField(max_length=100, db_column='paymentId', blank=True, null=True)
    status = models.CharField(max_length=50, default='Completed')
    memo = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'payments'

class Quotation(models.Model):
    id = models.CharField(primary_key=True, max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column='user_id')
    quoteNumber = models.CharField(max_length=100, db_column='quoteNumber')
    client = models.ForeignKey(Client, on_delete=models.CASCADE, db_column='clientId')
    status = models.CharField(max_length=50)
    createdDate = models.CharField(max_length=100, db_column='createdDate')
    validUntilDate = models.CharField(max_length=100, db_column='validUntilDate')
    subTotal = models.FloatField(db_column='subTotal')
    discount = models.FloatField(default=0)
    taxRate = models.FloatField(default=0, db_column='taxRate')
    taxAmount = models.FloatField(default=0, db_column='taxAmount')
    totalDue = models.FloatField(db_column='totalDue')
    terms = models.TextField(blank=True, null=True)
    footer = models.TextField(blank=True, null=True)
    title = models.CharField(max_length=255, blank=True, null=True)
    allowComments = models.IntegerField(default=0, db_column='allowComments')
    reasonForDecline = models.TextField(db_column='reasonForDecline', blank=True, null=True)

    class Meta:
        db_table = 'quotations'

class QuotationItem(models.Model):
    id = models.CharField(primary_key=True, max_length=100)
    quotation = models.ForeignKey(Quotation, on_delete=models.CASCADE, db_column='quotation_id', related_name='items')
    qty = models.FloatField()
    title = models.CharField(max_length=255)
    adjustPercent = models.FloatField(default=0, db_column='adjustPercent')
    rate = models.FloatField()
    amount = models.FloatField()
    description = models.TextField(blank=True, null=True)
    taxable = models.IntegerField(default=1)

    class Meta:
        db_table = 'quotation_items'

class Settings(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, db_column='user_id')
    settings_json = models.TextField(db_column='settings_json')

    class Meta:
        db_table = 'settings'

class Log(models.Model):
    id = models.CharField(primary_key=True, max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column='user_id')
    timestamp = models.CharField(max_length=100)
    eventType = models.CharField(max_length=100, db_column='eventType')
    description = models.TextField()
    details = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'logs'

class SentEmail(models.Model):
    id = models.CharField(primary_key=True, max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column='user_id')
    timestamp = models.CharField(max_length=100)
    recipient_to = models.TextField(db_column='recipient_to')
    subject = models.TextField()
    body = models.TextField()
    buttonText = models.TextField(db_column='buttonText', blank=True, null=True)
    buttonUrl = models.TextField(db_column='buttonUrl', blank=True, null=True)

    class Meta:
        db_table = 'sent_emails'
