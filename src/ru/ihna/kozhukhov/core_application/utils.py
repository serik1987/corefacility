from django.conf import settings
from django.template.loader import get_template
from django.template.exceptions import TemplateDoesNotExist
from django.core.mail import EmailMultiAlternatives


def mail(template_prefix: str = None, context_data=None, subject: str = "Test message", recipient: str = None, fail_silently=False):
	"""
	Sends an e-mail using the template. The function if different from
	django.core.mail.send_mail because it doesn't require the mail body.
	Instead, it requires the template and context. The function generates the mail
	body using default Django template renderer
	:param template_prefix: template files prefix. Template files must have the following
	name: <prefix>.<lang-code>.<extension>. where <prefix is value of this argument,
	lang-code is value of django.conf.settings.LANGUAGE_CODE and <extension> is
	'txt' and 'html' (both template files must exist)
	:param context_data: the context to be substituted
	:param subject: Mail's subject
	:param recipient: Mail's recipient
	:param fail_silently: If True, the function will not throw an exception in case when mail send fails,
	:return: None
	"""
	if context_data is None:
		context_data = {}
	plain_template = "%s.%s.%s" % (template_prefix, settings.LANGUAGE_CODE, "txt")
	html_template = "%s.%s.%s" % (template_prefix, settings.LANGUAGE_CODE, "html")
	try:
		plain_text = get_template(plain_template).render(context_data)
		html = get_template(html_template).render(context_data)
	except TemplateDoesNotExist:
		plain_text = get_template("%s.en-GB.txt" % template_prefix).render(context_data)
		html = get_template("%s.en-GB.html" % template_prefix).render(context_data)
	mail_object = EmailMultiAlternatives(subject, plain_text, None, [recipient])
	mail_object.attach_alternative(html, "text/html")
	result = mail_object.send(fail_silently)
	print(result)


def get_ip(request):
	"""
	Returns the current IP address
	:param request: the request which IP address must be returned
	:return: a string containing the IP address
	"""
	if "HTTP_X_FORWARDED_FOR" in request.META:
		x_forwarded_for = request.META['HTTP_X_FORWARDED_FOR'].split(",", 1)
		ip_address = x_forwarded_for[0]
	else:
		ip_address = request.META['REMOTE_ADDR']
	return ip_address
