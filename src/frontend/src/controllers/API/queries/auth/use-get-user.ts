import type { UseMutationResult } from "@tanstack/react-query";
import useAuthStore from "@/stores/authStore";
import type { Users, useMutationFunctionType } from "../../../../types/api";
import { api } from "../../api";
import { getURL } from "../../helpers/constants";
import { UseRequestProcessor } from "../../services/request-processor";
import { getMe, clearMeCache } from "@/lib/me";
export const useGetUserData: useMutationFunctionType<undefined, any> = (
  options?,
) => {
  const setUserData = useAuthStore((state) => state.setUserData);
  const { mutate } = UseRequestProcessor();

  const getUserData = async () => {
    try {
      const userData = await getMe();
      setUserData(userData);
      return userData;
    } catch (error) {
      // If cached version fails, try fresh request
      const response = await api.get<Users>(`${getURL("USERS")}/whoami`);
      setUserData(response["data"]);
      return response["data"];
    }
  };

  const mutation: UseMutationResult = mutate(
    ["useGetUserData"],
    getUserData,
    options,
  );

  return mutation;
};
