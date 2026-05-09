/**
 * Backwards-compatible wrapper around the generic catalogue browser.
 * Existing callers (`/`, `/l1/[slug]`) keep working unchanged; the heavy
 * lifting now lives in `./catalog/CatalogBrowser.tsx`.
 */
import CatalogBrowser from "./catalog/CatalogBrowser";
import type { FlatNode, ValueStream } from "./catalog/types";

export type { FlatNode as FlatCap, ValueStream } from "./catalog/types";
export type { ValueStreamStage } from "./catalog/types";

interface Props {
  data: FlatNode[];
  valueStreams: ValueStream[];
}

export default function CatalogueBrowser({ data, valueStreams }: Props) {
  return <CatalogBrowser kind="capability" data={data} valueStreams={valueStreams} />;
}
