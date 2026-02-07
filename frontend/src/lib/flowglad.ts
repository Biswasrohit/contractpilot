import { FlowgladServer } from "@flowglad/server";

export const flowglad = (customerExternalId: string) => {
  return new FlowgladServer({
    apiKey: process.env.FLOWGLAD_SECRET_KEY!,
    customerExternalId,
    getCustomerDetails: async (externalId: string) => {
      return {
        email: `${externalId}@contractpilot.app`,
        name: externalId,
      };
    },
  });
};
