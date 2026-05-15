import esper
from typing import final, override
from client.component import Lifetime


@final
class LifetimeProc(esper.Processor):
    @override
    def process(self, dt: float):
        for ent, (life) in esper.get_component(Lifetime):
            life.time -= dt

            if life.time <= 0:
                esper.delete_entity(ent)
