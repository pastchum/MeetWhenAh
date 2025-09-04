import { useEffect, useMemo, useState } from "react";
import User from "../types/User";
import { atom, useAtom } from "jotai";

const userAtom = atom<User | null>(null);

const useUser = (tele_id?: string) => {
  const [user, setUser] = useAtom(userAtom);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    if (!tele_id) {
        setLoading(false);
        return;
    }

        const fetchUser = async () => {
        try {
            const response = await fetch(`/api/user/${tele_id}`);
            if (!response.ok) {
            throw new Error("Failed to fetch user");
            }
            const data = await response.json();
            setUser(data);
        } catch (error) {
            setError(error as Error);
        } finally {
            setLoading(false);
            }
        };
        fetchUser();
    
  }, [tele_id]);

  const updateUser = async (data: Partial<User>) => {
    try {
      const response = await fetch(`/api/user/update/${user?.uuid}`, {
        method: "PUT",
        body: JSON.stringify(data),
      });
      if (!response.ok) {
        throw new Error("Failed to update user");
      }
      const updatedUser = await response.json();
      setUser(updatedUser);
    } catch (error) {
      setError(error as Error);
      return null;
    }
  };

  const createUser = async (data: User) => {
    try {
      const response = await fetch("/api/user/create", {
        method: "POST",
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        throw new Error("Failed to create user");
      }
      const createdUser = await response.json();
      setUser(createdUser);
      return createdUser;
    }
    catch (error) {
      setError(error as Error);
      return null;
    }
  };

  const deleteUser = async () => {
    try {
      const response = await fetch(`/api/user/delete/${user?.uuid}`, {
        method: "DELETE",
      });
      if (!response.ok) {
        throw new Error("Failed to delete user");
      }
      setUser(null);
      return true;
    }
    catch (error) {
      setError(error as Error);
      return null;
    }
  };

  const userToReturn = useMemo(() => {
    if (tele_id && tele_id != user?.tele_id) {
      return null;
    }
    return user;
  }, [tele_id, user]);

  return { user: userToReturn, loading, error, updateUser, createUser, deleteUser };
};

export default useUser;