from django import template
from django.utils import timezone
from django.utils.safestring import mark_safe
import markdown
from markdown.extensions import Extension
from markdown.treeprocessors import Treeprocessor

register = template.Library()

class TailwindTreeprocessor(Treeprocessor):
    def run(self, root):
        tag_classes = {
            'h1': 'text-3xl font-extrabold bg-gradient-to-r from-teal-600 to-emerald-600 bg-clip-text text-transparent mb-4 mt-6 pb-2 border-b-2 border-teal-200',
            'h2': 'text-2xl font-bold text-gray-900 mb-4 mt-6 pb-2 border-b-2 border-gray-200',
            'h3': 'text-xl font-bold text-gray-800 mb-3 mt-5',
            'h4': 'text-lg font-semibold text-gray-800 mb-2 mt-4',
            'h5': 'text-base font-semibold text-gray-700 mb-2 mt-3',
            'h6': 'text-sm font-semibold text-gray-700 mb-2 mt-2',
            'p': 'text-gray-700 text-base mb-4 leading-relaxed',
            'ul': 'list-disc list-outside mb-4 space-y-2 pl-6',
            'ol': 'list-decimal list-outside mb-4 space-y-2 pl-6',
            'li': 'text-gray-700 text-base leading-relaxed ml-2',
            'a': 'text-teal-600 hover:text-teal-700 font-medium underline decoration-2 decoration-teal-300 hover:decoration-teal-500 transition-all duration-200',
            'blockquote': 'border-l-4 border-teal-500 bg-gradient-to-r from-teal-50 to-emerald-50 pl-4 pr-3 py-3 italic text-gray-700 my-4 rounded-r-lg shadow-sm text-base',
            'code': 'bg-gray-100 text-pink-600 px-2 py-0.5 rounded-md text-sm font-mono border border-gray-200',
            'pre': 'bg-gray-900 text-gray-100 p-4 rounded-xl overflow-x-auto mb-4 shadow-lg border border-gray-700 text-sm',
            'table': 'w-full border-collapse bg-white shadow-md rounded-lg overflow-hidden mb-4 text-sm',
            'thead': 'bg-gradient-to-r from-teal-600 to-emerald-600',
            'th': 'px-4 py-3 text-left text-xs font-bold text-white uppercase tracking-wider',
            'tbody': 'divide-y divide-gray-200',
            'tr': 'hover:bg-gray-50 transition-colors duration-150',
            'td': 'px-4 py-3 text-sm text-gray-700',
            'img': 'rounded-2xl shadow-xl my-4 max-w-full h-auto border-4 border-gray-100',
            'hr': 'my-6 border-t-2 border-gray-200',
            'strong': 'font-bold text-gray-900',
            'em': 'italic text-gray-700',
        }

        for element in root.iter():
            if element.tag in tag_classes:
                existing_class = element.get('class', '')
                new_class = tag_classes[element.tag]
                element.set('class', f'{existing_class} {new_class}'.strip())

        return root


class TailwindExtension(Extension):
    def extendMarkdown(self, md):
        md.treeprocessors.register(TailwindTreeprocessor(md), 'tailwind', 15)


@register.filter(name='markdown')
def markdown_format(text):
    md = markdown.Markdown(extensions=[
        'markdown.extensions.extra',
        'markdown.extensions.codehilite',
        'markdown.extensions.tables',
        'markdown.extensions.fenced_code',
        TailwindExtension(),
    ])

    html = md.convert(str(text))
    return mark_safe(html)


@register.filter(name='currency')
def currency(value, currency='грн'):
	try:
		value = float(value)
		if value.is_integer():
			formatted = f"{int(value):,}".replace(',', ' ')
		else:
			formatted = f"{value:,.2f}".replace(',', ' ').replace('.', ',')
		return f"{formatted} {currency}"
	except (ValueError, TypeError):
		return value

@register.filter
def time_ago(date):
	if not date:
		return ""

	now = timezone.now()
	diff = now - date
	seconds = diff.total_seconds()

	if seconds < 60:
		return "щойно"
	elif seconds < 3600:
		minutes = int(seconds / 60)
		return f"{minutes} хв тому"
	elif seconds < 86400:
		hours = int(seconds / 3600)
		return f"{hours} год тому"
	elif seconds < 604800:
		days = int(seconds / 86400)
		return f"{days} дн тому"
	else:
		return date.strftime("%d.%m.%Y")