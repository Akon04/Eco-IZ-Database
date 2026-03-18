import { z } from "zod";

export const loginSchema = z.object({
  email: z.string().email("Enter a valid email address."),
  password: z
    .string()
    .min(6, "Password must be at least 6 characters long."),
});

export const userFormSchema = z.object({
  role: z.enum(["USER", "MODERATOR", "ADMIN"]),
  status: z.enum(["ACTIVE", "REVIEW", "SUSPENDED"]),
  adminNote: z
    .string()
    .min(8, "Add a short admin note with at least 8 characters."),
});

export const categoryFormSchema = z.object({
  name: z.string().min(2, "Category name must be at least 2 characters."),
  description: z
    .string()
    .min(8, "Description must be at least 8 characters long."),
  color: z.string().min(3, "Color value must be at least 3 characters."),
  icon: z.string().min(2, "Icon value must be at least 2 characters."),
});

export const habitFormSchema = z.object({
  title: z.string().min(2, "Habit title must be at least 2 characters."),
  category: z.string().min(2, "Select a valid category."),
  points: z.coerce.number().min(0, "Points cannot be negative."),
  co2Value: z.coerce.number().min(0, "CO2 value cannot be negative."),
  waterValue: z.coerce.number().min(0, "Water value cannot be negative."),
  energyValue: z.coerce.number().min(0, "Energy value cannot be negative."),
});

export const achievementFormSchema = z.object({
  title: z.string().min(2, "Achievement title must be at least 2 characters."),
  description: z
    .string()
    .min(8, "Description must be at least 8 characters long."),
  icon: z.string().min(2, "Icon value must be at least 2 characters."),
  targetValue: z.coerce.number().min(1, "Target value must be at least 1."),
  rewardPoints: z.coerce.number().min(0, "Reward points cannot be negative."),
});

export const postFormSchema = z.object({
  visibility: z.enum(["PUBLIC", "FOLLOWERS", "PRIVATE"]),
  state: z.enum(["Published", "Flagged", "Needs review", "Hidden"]),
  moderatorNote: z
    .string()
    .min(8, "Moderator note must be at least 8 characters long."),
});

export type LoginFormValues = z.infer<typeof loginSchema>;
export type UserFormValues = z.infer<typeof userFormSchema>;
export type CategoryFormValues = z.infer<typeof categoryFormSchema>;
export type HabitFormValues = z.infer<typeof habitFormSchema>;
export type AchievementFormValues = z.infer<typeof achievementFormSchema>;
export type PostFormValues = z.infer<typeof postFormSchema>;
