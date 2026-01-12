create table books (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references auth.users not null,
  title text not null,
  author text,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

create table notes (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references auth.users not null
  book_id uuid references books(id) on delete cascade,
  
  content text,
  page_number integer,
  quote text,
  comment text,
  tags text[],
  confidence_score float,
  
  created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- ENABLE ROW LEVEL SECURITY (RLS)
alter table books enable row level security;
alter table notes enable row level security;

-- Create Policies for BOOKS
create policy "Users can select their own books"
on books for select using (auth.uid() = user_id);

create policy "Users can insert their own books"
on books for insert with check (auth.uid() = user_id);

create policy "Users can update their own books"
on books for update using (auth.uid() = user_id);

create policy "Users can delete their own books"
on books for delete using (auth.uid() = user_id);

-- Create Policies for NOTES
create policy "Users can select their own notes"
on notes for select using (auth.uid() = user_id);

create policy "Users can insert their own notes"
on notes for insert with check (auth.uid() = user_id);

create policy "Users can update their own notes"
on notes for update using (auth.uid() = user_id);

create policy "Users can delete their own notes"
on notes for delete using (auth.uid() = user_id);