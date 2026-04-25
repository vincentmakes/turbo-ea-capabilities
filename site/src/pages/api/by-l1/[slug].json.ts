import type { APIRoute, GetStaticPaths } from "astro";
import { l1List } from "../../../data/load.ts";

export const prerender = true;

export const getStaticPaths: GetStaticPaths = () =>
  l1List().map(({ slug, root }) => ({
    params: { slug },
    props: { root },
  }));

export const GET: APIRoute = ({ props }) =>
  new Response(JSON.stringify(props.root, null, 2), {
    headers: {
      "content-type": "application/json; charset=utf-8",
      "cache-control": "public, max-age=300, s-maxage=86400",
    },
  });
