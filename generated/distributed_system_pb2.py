# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: distributed_system.proto
# Protobuf Python Version: 5.27.2
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    5,
    27,
    2,
    '',
    'distributed_system.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x18\x64istributed_system.proto\x12\x0b\x64istributed\"~\n\x0c\x43lockMessage\x12\x11\n\tsender_id\x18\x01 \x01(\x05\x12\x15\n\rlogical_clock\x18\x02 \x01(\x05\x12\x1a\n\x12sender_system_time\x18\x03 \x01(\x01\x12\x14\n\x0cqueue_length\x18\x04 \x01(\x05\x12\x12\n\nevent_type\x18\x05 \x01(\t\"\x15\n\x03\x41\x63k\x12\x0e\n\x06status\x18\x01 \x01(\t2O\n\x11\x44istributedSystem\x12:\n\x0bSendMessage\x12\x19.distributed.ClockMessage\x1a\x10.distributed.Ackb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'distributed_system_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_CLOCKMESSAGE']._serialized_start=41
  _globals['_CLOCKMESSAGE']._serialized_end=167
  _globals['_ACK']._serialized_start=169
  _globals['_ACK']._serialized_end=190
  _globals['_DISTRIBUTEDSYSTEM']._serialized_start=192
  _globals['_DISTRIBUTEDSYSTEM']._serialized_end=271
# @@protoc_insertion_point(module_scope)
