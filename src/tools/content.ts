/**
 * Content management tools for CC5 (clothing, hair, accessories).
 */

import { z } from "zod";
import type { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import type { CC5Bridge } from "../cc5-bridge.js";
import { bridgeCall } from "../util.js";

export function registerContentTools(server: McpServer, bridge: CC5Bridge) {
  server.tool(
    "list_clothes",
    "List all clothing items currently worn by the avatar. Returns name, ID, and type for each item.",
    {},
    async () => bridgeCall(
      () => bridge.listClothes(),
      (clothes) => {
        if (clothes.length === 0) {
          return "No clothing items on the avatar.";
        }
        const lines = clothes.map(c => `- ${c.name} (ID: ${c.id}, Type: ${c.type})`);
        return `Found ${clothes.length} clothing item(s):\n${lines.join("\n")}`;
      },
    )
  );

  server.tool(
    "list_hair",
    "List all hair items on the current avatar. Returns name, ID, and type for each item.",
    {},
    async () => bridgeCall(
      () => bridge.listHair(),
      (hairs) => {
        if (hairs.length === 0) {
          return "No hair items on the avatar.";
        }
        const lines = hairs.map(h => `- ${h.name} (ID: ${h.id}, Type: ${h.type})`);
        return `Found ${hairs.length} hair item(s):\n${lines.join("\n")}`;
      },
    )
  );

  server.tool(
    "list_accessories",
    "List all accessories on the current avatar. Returns name and ID for each item.",
    {},
    async () => bridgeCall(
      () => bridge.listAccessories(),
      (accessories) => {
        if (accessories.length === 0) {
          return "No accessories on the avatar.";
        }
        const lines = accessories.map(a => `- ${a.name} (ID: ${a.id})`);
        return `Found ${accessories.length} accessory(ies):\n${lines.join("\n")}`;
      },
    )
  );

  server.tool(
    "remove_scene_item",
    "Remove a clothing, hair, or accessory item from the avatar by name. Use list_clothes, list_hair, or list_accessories first to find item names.",
    {
      item_name: z.string().max(256).describe("Name of the item to remove"),
    },
    async ({ item_name }) => bridgeCall(
      () => bridge.removeSceneItem(item_name),
      (result) => result.success
        ? `Removed item: ${result.removed}`
        : `Failed: ${result.error}`,
    )
  );

  server.tool(
    "content_folders",
    "Diagnostic for browse_content: shows the raw CC5 content folder strings ('$/...' virtual and the custom disk folder), their file counts and subfolders for one EContentRootFolder name (e.g. Coats, Character, Shoes).",
    { folder_type: z.string().max(64).describe("EContentRootFolder suffix, e.g. Coats, Character, Shoes, Upper") },
    async ({ folder_type }) => bridgeCall(
      () => bridge.contentFolders(folder_type),
      (r) => JSON.stringify(r, null, 2),
    )
  );

  server.tool(
    "browse_content",
    "Browse available CC5 content files by category. Returns file paths that can be loaded with load_asset. Wearables: cloth_upper, cloth_lower, cloth, shoes, accessory_head, accessory_body. Garment library: coats, shirts, pants, skirts, gloves, underwear, cloth_others. Scene/animation: pose, motion, expression, props, light, camera, character. Also skin, persona, mixer_full_character. Searches subfolders.",
    {
      folder_type: z.enum([
        "cloth_upper", "cloth_lower", "cloth", "shoes", "accessory_head", "accessory_body",
        "pose", "motion", "expression", "props", "light", "camera", "character",
        "coats", "shirts", "pants", "skirts", "gloves", "underwear", "cloth_others",
        "skin", "persona", "mixer_full_character",
      ]).default("cloth_upper")
        .describe("Content category. Wearables: cloth_upper/cloth_lower/cloth/shoes/accessory_head/accessory_body. Scene & animation: pose/motion/expression/props/light/camera/character. Load a returned path with load_asset."),
    },
    async ({ folder_type }) => bridgeCall(
      () => bridge.browseContent(folder_type),
      (files) => {
        if (files.length === 0) {
          return `No content files found for category '${folder_type}'.`;
        }
        // Check if the first entry is an error message
        if (files.length === 1 && (files[0].startsWith("Unknown folder") || files[0].startsWith("Error") || files[0].startsWith("Content browsing"))) {
          return files[0];
        }
        const display = files.slice(0, 50);
        let text = `Found ${files.length} content file(s) for '${folder_type}':\n`;
        text += display.map(f => `- ${f}`).join("\n");
        if (files.length > 50) {
          text += `\n... and ${files.length - 50} more`;
        }
        return text;
      },
    )
  );
}
