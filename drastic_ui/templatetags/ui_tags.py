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

@register.tag(name="percentage_color")
def percentage_color(parser, token):
    try:
        tag_name, total, used = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(
            "%r tag requires exactly two arguments" % token.contents.split()[0]
        )
    return PercentageColorNode(total, used)


class PercentageNode(template.Node):
    def __init__(self, total, used):
        self.total = template.Variable(total)
        self.used   = template.Variable(used)

    def render(self, context):
        try:
            actual_total = self.total.resolve(context)
            actual_used = self.used.resolve(context)
        except template.VariableDoesNotExist:
            return ''

        return 100 / (actual_total / actual_used)

class PercentageColorNode(template.Node):
    def __init__(self, total, used):
        self.total = template.Variable(total)
        self.used   = template.Variable(used)

    def render(self, context):
        try:
            actual_total = self.total.resolve(context)
            actual_used = self.used.resolve(context)
        except template.VariableDoesNotExist:
            return ''

        pc = (100 / (actual_total / actual_used))
        if pc < 50:
            return 'success'
        if pc < 75:
            return 'warning'
        return 'danger'
