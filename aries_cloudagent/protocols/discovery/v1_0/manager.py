"""."""
import logging

from aries_cloudagent.protocols.discovery.v1_0.messages.query import Query

from ....config.injection_context import InjectionContext
from ....core.error import BaseError
from ....core.profile import Profile
from ....core.protocol_registry import ProtocolRegistry
from ....storage.error import StorageNotFoundError
from ....messaging.responder import BaseResponder

from .messages.disclose import Disclose
from .models.discovery_record import V10DiscoveryExchangeRecord


class V10DiscoveryMgrError(BaseError):
    """Discover feature v1_0 error."""


class V10DiscoveryMgr:
    """Class for discover feature v1_0 under RFC 31."""

    def __init__(self, profile: Profile):
        """
        Initialize a V10DiscoveryMgr.

        Args:
            profile: The profile for this manager
        """
        self._profile = profile
        self._logger = logging.getLogger(__name__)

    @property
    def profile(self) -> Profile:
        """
        Accessor for the current Profile.

        Returns:
            The Profile for this manager

        """
        return self._profile

    async def receive_disclose(
        self, disclose_msg: Disclose
    ) -> V10DiscoveryExchangeRecord:
        """Receive Disclose message and return updated V10DiscoveryExchangeRecord."""
        thread_id = disclose_msg._thread.thid
        async with self._profile.session() as session:
            discover_exch_rec = await V10DiscoveryExchangeRecord.retrieve_by_thread_id(
                session=session, thread_id=thread_id
            )
        discover_exch_rec.disclose = disclose_msg
        return discover_exch_rec

    async def receive_query(self, base_context: InjectionContext) -> Disclose:
        """Process query and return the corresponding disclose message."""
        registry = base_context.inject(ProtocolRegistry)
        query_msg = base_context.message.query
        protocols = registry.protocols_matching_query(query_msg)
        result = await registry.prepare_disclosed(base_context, protocols)
        disclose_msg = Disclose(protocols=result)
        disclose_msg.assign_thread_id(query_msg._thread.thid)
        return disclose_msg

    async def create_and_send_query(
        self, connection_id: str, query: str, comment: str = None
    ) -> V10DiscoveryExchangeRecord:
        """Create and send a Query message."""
        async with self._profile.session() as session:
            try:
                # If existing record exists for a connection_id
                existing_discovery_ex_rec = (
                    await V10DiscoveryExchangeRecord.retrieve_by_connection_id(
                        session=session, connection_id=connection_id
                    )
                )
                await existing_discovery_ex_rec.delete_record(session)
                existing_discovery_ex_rec = V10DiscoveryExchangeRecord()
            except StorageNotFoundError:
                existing_discovery_ex_rec = V10DiscoveryExchangeRecord()
        query_msg = Query(query=query, comment=comment)
        existing_discovery_ex_rec.query = query_msg
        existing_discovery_ex_rec.comment = comment
        responder = self.profile.inject_or(BaseResponder)
        if responder:
            await responder.send(query_msg, connection_id=connection_id)
        else:
            self._logger.exception(
                "Unable to send discover-features v1 query message"
                ": BaseResponder unavailable"
            )
        return existing_discovery_ex_rec
