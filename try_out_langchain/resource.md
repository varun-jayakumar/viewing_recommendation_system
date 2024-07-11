# What is langchain

- Think of Langchain as a wrapper aroung LLMs

## Format: a prompt with valiables:

- as in it just replaces things in a template to format it into a single prompt

## Predict: Get initial output form LLM

- in this phase we put the prompt that we format and give it to a LLM
- then the LLM with gen an output - this is called the predict phase

## Parse:

- at this phase the output that we got from LLM will be reformatted and we can parse it into however we want, this will help us leverge the output to write business logic with
