from fastapi import Depends
from sqlalchemy import select
from sqlmodel.ext.asyncio.session import AsyncSession

from db.postgres import get_async_session
from models.tariff import TariffModel
from schemas.tariff import TariffSchema


class TariffService:

    def __init__(self, session):
        self.session = session

    async def get_active_tariffs(self) -> list[TariffSchema]:
        query = await self.session.execute(select(TariffModel).where(TariffModel.is_active == True))
        tariffs = []
        for tariff in query.scalars().all():
            tariffs.append(
                TariffSchema(
                    id=tariff.id,
                    name=tariff.name,
                    description=tariff.description,
                    price=tariff.price
                )
            )
        return tariffs


def get_tariff_service(
        session: AsyncSession = Depends(get_async_session)
):
    return TariffService(session)
