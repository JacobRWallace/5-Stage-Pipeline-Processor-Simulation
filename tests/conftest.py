import pytest

from pipeline_sim import Config, Pipeline, parse_program


def simulate(src, regs=None, mem=None, **cfg):
    return Pipeline(parse_program(src), Config(**cfg), regs=regs, mem=mem).run()


@pytest.fixture
def sim():
    return simulate
