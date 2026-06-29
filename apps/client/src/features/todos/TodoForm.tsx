import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Plus, LoaderCircle } from "lucide-react";
import { toast } from "sonner";
import type { z } from "zod";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { createTodoSchema } from "@/schemas/todo";
import { useCreateTodo } from "./hooks";

// Input has optional `completed` (it has a default); output/transformed has it required.
type TodoFormInput = z.input<typeof createTodoSchema>;
type TodoFormValues = z.output<typeof createTodoSchema>;

export function TodoForm() {
  const createTodo = useCreateTodo();

  const form = useForm<TodoFormInput, unknown, TodoFormValues>({
    resolver: zodResolver(createTodoSchema),
    defaultValues: { title: "", completed: false },
  });

  const onSubmit = (values: TodoFormValues) => {
    createTodo.mutate(values, {
      onSuccess: () => {
        form.reset({ title: "", completed: false });
      },
      onError: () => {
        toast.error("Could not add todo. Please try again.");
      },
    });
  };

  return (
    <Form {...form}>
      <form
        onSubmit={form.handleSubmit(onSubmit)}
        className="flex flex-col gap-2 sm:flex-row sm:items-start"
        aria-label="Add todo"
        noValidate
      >
        <FormField
          control={form.control}
          name="title"
          render={({ field }) => (
            <FormItem className="flex-1">
              <FormLabel>Title</FormLabel>
              <FormControl>
                <Input
                  placeholder="What needs to be done?"
                  autoComplete="off"
                  {...field}
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <Button
          type="submit"
          className="sm:mt-7"
          disabled={createTodo.isPending}
        >
          {createTodo.isPending ? (
            <LoaderCircle className="animate-spin" aria-hidden="true" />
          ) : (
            <Plus aria-hidden="true" />
          )}
          Add
        </Button>
      </form>
    </Form>
  );
}
