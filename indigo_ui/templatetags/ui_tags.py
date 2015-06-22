from django import template

register = template.Library()

@register.assignment_tag
def get_bootstrap_alert_msg_css_name(tags):
    return 'danger' if tags == 'error' else tags

@register.tag(name="percentage")
def percentage(parser, token):
    try:
        tag_name, total, used = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(
            "%r tag requires exactly two arguments" % token.contents.split()[0]
        )
    return PercentageNode(total, used)


class PercentageNode(template.Node):
    def __init__(self, total, used):
        self.total = template.Variable(total)
        self.used   = template.Variable(used)

    def render(self, context):
        try:
            actual_total = self.total.resolve(context)
            actual_used = self.used.resolve(context)
            print actual_used, actual_total
        except template.VariableDoesNotExist:
            return ''

        return 100 / (actual_total / actual_used)