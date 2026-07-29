// SPDX-License-Identifier: MIT
/**
 * Canonical hash of an artefact node's translatable surface.
 *
 * Sidecar entries optionally store `source_hash`. When present, lint
 * recomputes the hash from the current English source and compares; a
 * mismatch means the sidecar entry is stale and must be retranslated.
 *
 * The translatable-fields whitelist (per business-capability-governance-model.md):
 *   - capability / business-process: name, description, aliases, in_scope, out_of_scope
 *   - value-stream stream-level: name, description
 *   - value-stream stage-level: stage_name, description, notes
 *
 * Hash format: 'sha256-' + first 16 hex chars of SHA-256 over canonical JSON.
 * Algorithm prefix is reserved so the format can evolve later without
 * silent collisions.
 */
import { createHash } from "node:crypto";

const HASH_PREFIX = "sha256-";

function canonicalJson(fields: Record<string, unknown>): string {
  const keys = Object.keys(fields).sort();
  const out: Record<string, unknown> = {};
  for (const k of keys) {
    const v = fields[k];
    out[k] = v === undefined ? null : v;
  }
  return JSON.stringify(out);
}

function digest(json: string): string {
  return HASH_PREFIX + createHash("sha256").update(json).digest("hex").slice(0, 16);
}

export interface CapabilityLikeSource {
  name: string;
  description?: string;
  aliases?: string[];
  in_scope?: string[];
  out_of_scope?: string[];
}

export function hashCapabilityLikeSource(node: CapabilityLikeSource): string {
  return digest(
    canonicalJson({
      name: node.name,
      description: node.description ?? null,
      aliases: node.aliases ?? null,
      in_scope: node.in_scope ?? null,
      out_of_scope: node.out_of_scope ?? null,
    })
  );
}

export interface ValueStreamSource {
  name: string;
  description?: string;
}

export function hashValueStreamSource(stream: ValueStreamSource): string {
  return digest(
    canonicalJson({
      name: stream.name,
      description: stream.description ?? null,
    })
  );
}

export interface ValueStreamStageSource {
  stage_name: string;
  description?: string;
  notes?: string;
}

export function hashValueStreamStageSource(stage: ValueStreamStageSource): string {
  return digest(
    canonicalJson({
      stage_name: stage.stage_name,
      description: stage.description ?? null,
      notes: stage.notes ?? null,
    })
  );
}

export interface MacroCapabilitySource {
  name: string;
  description?: string;
  in_scope?: string[];
  out_of_scope?: string[];
}

export function hashMacroCapabilitySource(macro: MacroCapabilitySource): string {
  return digest(
    canonicalJson({
      name: macro.name,
      description: macro.description ?? null,
      in_scope: macro.in_scope ?? null,
      out_of_scope: macro.out_of_scope ?? null,
    })
  );
}
