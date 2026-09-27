"""JSON-RPC 2.0 framing and streaming server for LSP diagnostics (Story 20.3).

Drivers: ArgusAgent-FR-39 (IDE & LSP diagnostic surface), AR10 (typed failure / zero panic),
AR8 (PURE framing logic, explicit stream injection).

Why this module exists
----------------------
Framing and streaming engine for JSON-RPC 2.0 `textDocument/publishDiagnostics`
notifications. Wraps diagnostic payloads with standard LSP `Content-Length` headers
and streams them over stdio or socket transports with graceful exception handling.
"""

from __future__ import annotations

import socket
from collections.abc import Sequence
from typing import TYPE_CHECKING, BinaryIO, TextIO

from argus.adapters.lsp.adapter import LSPDiagnosticAdapter
from argus.adapters.lsp.models import JSONRPCNotification, PublishDiagnosticsParams

if TYPE_CHECKING:
    from argus.ledger.recording import Recording

__all__ = [
    "format_jsonrpc_message",
    "LSPDiagnosticServer",
]


def format_jsonrpc_message(notification: JSONRPCNotification) -> str:
    """Format a JSONRPCNotification into standard LSP header-framed string format.

    Header format: ``Content-Length: <byte_length>\r\n\r\n<json_payload>``
    The Content-Length specifies the UTF-8 byte length of the JSON payload.
    """
    json_payload = notification.model_dump_json(exclude_none=True)
    payload_bytes = json_payload.encode("utf-8")
    content_length = len(payload_bytes)
    return f"Content-Length: {content_length}\r\n\r\n{json_payload}"


class LSPDiagnosticServer:
    """Streaming server publishing LSP diagnostic notifications over stdio or sockets."""

    @staticmethod
    def publish_diagnostics(
        stream: TextIO | BinaryIO | socket.socket,
        params: PublishDiagnosticsParams,
    ) -> int:
        """Publish a single `PublishDiagnosticsParams` notification to the stream.

        Returns the number of UTF-8 bytes transmitted. Handles stream IO errors gracefully.
        """
        notification = JSONRPCNotification(params=params)
        message_str = format_jsonrpc_message(notification)
        message_bytes = message_str.encode("utf-8")

        try:
            if isinstance(stream, socket.socket):
                stream.sendall(message_bytes)
                return len(message_bytes)

            # Check binary stream vs text stream
            try:
                written = stream.write(message_bytes)  # type: ignore[arg-type,call-overload]
                if hasattr(stream, "flush"):
                    stream.flush()
                return written if isinstance(written, int) else len(message_bytes)
            except TypeError:
                # Fallback to text stream write
                stream.write(message_str)  # type: ignore[arg-type,call-overload]
                if hasattr(stream, "flush"):
                    stream.flush()
                return len(message_bytes)
        except (OSError, BrokenPipeError, ConnectionResetError, ValueError):
            # Gracefully swallow closed/broken stream errors without process panic (AR10)
            return 0

    @classmethod
    def publish_recordings(
        cls,
        stream: TextIO | BinaryIO | socket.socket,
        recordings: Sequence[Recording],
        workspace_root: str = ".",
    ) -> int:
        """Batch publish Argus recordings aggregated by document URI.

        Returns total bytes written.
        """
        by_uri = LSPDiagnosticAdapter.map_recordings_by_uri(recordings, workspace_root)
        total_bytes = 0
        for uri, diagnostics in by_uri.items():
            params = PublishDiagnosticsParams(uri=uri, diagnostics=diagnostics)
            bytes_written = cls.publish_diagnostics(stream, params)
            total_bytes += bytes_written
        return total_bytes
