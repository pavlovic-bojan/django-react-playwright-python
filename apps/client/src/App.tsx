import { QueryClientProvider } from "@tanstack/react-query";

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Toaster } from "@/components/ui/sonner";
import { ErrorBoundary } from "@/components/ErrorBoundary";
import { queryClient } from "@/lib/query-client";
import { TodoForm } from "@/features/todos/TodoForm";
import { TodoList } from "@/features/todos/TodoList";

function App() {
  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <main className="mx-auto flex min-h-svh w-full max-w-xl flex-col gap-6 px-4 py-10">
          <header className="text-center">
            <h1 className="text-3xl font-semibold tracking-tight">Todos</h1>
          </header>

          <Card>
            <CardHeader>
              <CardTitle>Add a todo</CardTitle>
              <CardDescription>
                Keep track of what needs to get done.
              </CardDescription>
            </CardHeader>
            <CardContent className="flex flex-col gap-6">
              <TodoForm />
              <TodoList />
            </CardContent>
          </Card>
        </main>
        <Toaster />
      </QueryClientProvider>
    </ErrorBoundary>
  );
}

export default App;
