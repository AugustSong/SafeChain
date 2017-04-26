#!/usr/bin/env python3

import itertools

class Action:
    def __init__(self, channel_name, name, content, variables):
        Action.checkDefinitionErrors(channel_name, name, content, variables)

        self.channel_name = channel_name
        self.name = name
        self.input_requirements = content['input']
        self.definition = content['definition']

        if self.hasInvalidInput(variables):
            raise ValueError('[{0}] action {1} with invalid input'.format(channel_name, name))

    @classmethod
    def checkDefinitionErrors(cls, channel_name, name, content, variables):
        if 'definition' not in content:
            raise ValueError('[{0}] action {1} without definition'.format(channel_name, name))

        if 'input' not in content:
            raise ValueError('[{0}] action {1} without input'.format(channel_name, name))

        for input_requirement in content['input']:
            if 'type' not in input_requirement:
                raise ValueError('[{0}] action {1} input without type'.format(channel_name, name))

            if input_requirement['type'] == 'device':
                continue

            if (input_requirement['type'] == 'value' and
                'variable' in input_requirement and
                input_requirement['variable'] in variables):
                continue

            if (input_requirement['type'] == 'set' and
                'setValue' in input_requirement and
                len(input_requirement['setValue']) != 0):
                continue

            raise ValueError('[{0}] action {1} input defined improperly'.format(channel_name, name))

        for assignment in content['definition']:
            if 'device' not in assignment:
                raise ValueError('[{0}] action {1} definition without device'.format(channel_name, name))

            if 'variable' not in assignment:
                raise ValueError('[{0}] action {1} definition without variable'.format(channel_name, name))

            if 'value' not in assignment:
                raise ValueError('[{0}] action {1} definition without value'.format(channel_name, name))

            if (isinstance(assignment['device'], str) and
                assignment['device'].startswith('$') and
                assignment['device'][1:].isdigit()):
                continue

            if (isinstance(assignment['value'], str) and
                assignment['value'].startswith('$') and
                assignment['value'][1:].isdigit()):
                continue

            raise ValueError('[{0}] action {1} definition without proper input index'.format(channel_name, name))

        return None

    def genAllPossibleInputs(self, devices, variables):
        values = []
        for input_requirement in self.input_requirements:
            if input_requirement['type'] == 'device':
                value = devices
            elif input_requirement['type'] == 'value':
                variable_name = input_requirement['variable']
                variable = variables[variable_name]
                value = variable.getPossibleValues()
            elif input_requirement['type'] == 'set':
                value = input_requirement['setValue']
            else:
                raise ValueError('[{0}] action {1} with unknown input type'.format(channel_name, action_name))

            values.append(value)

        yield from itertools.product(*values)

    def hasInvalidInput(self, variables):
        for input_value in self.genAllPossibleInputs(['action_device'], variables):
            for assignment in self.definition:
                variable_name = assignment['variable']
                if isinstance(assignment['value'], str) and assignment['value'].startswith('$'):
                    index = int(assignment['value'][1:])
                    variable_value = input_value[index]
                else:
                    variable_value = assignment['value']

                variable = variables[variable_name]
                if variable.hasAssignmentErrors(variable_value):
                    return True

        return False



