import type { APIRoute, GetStaticPaths } from "astro";
import { flat } from "../../../data/load.ts";

export const prerender = true;

export const getStaticPaths: GetStaticPaths = () =>
  flat.map((c) => ({
    params: { id: c.id },
    props: { node: c },
  }));

export const GET: APIRoute = ({ props }) =>
  new Response(JSON.stringify(props.node, null, 2), {
    headers: {
      "content-type": "application/json; charset=utf-8",
      "cache-control": "public, max-age=300, s-maxage=86400",
    },
  });
