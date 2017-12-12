# Associative Entity Tests

It's a tale as old as time. You've got a many-to-many relationship in a database
and a gun to your head. Implement it correctly and you live to fight relational
databases another day. Implement it wrong and the last thing you'll see is your
brains making a quick exit from the front of your skull as the scene dims out
for the last time.

The ancient lore, passed down from the days of Codd and Date, has been to create
two tables equal in stature. Between them stands the great bulwark against
chaos, the center where rows from these tables can meet in peace, the purely
associative entity. The associative entity has no attributes of its own, no
agency -- it exists selflessly to serve as the glue binding the data tables.

Some have said the associative entity should have its own primary key! This
heresy, granting intrinsic meaning to its rows, shall be shown to serve no
purpose but to squander precious space and cycles. It is they whose light shall
be extinguished.

# Methodology
## Tables
Four tables exist in this world (\* indicates primary key). Please see
[schema.sql](schema.sql) for details.

* `people (id*, name)`: 1M rows
* `companies (id*, name)`: 1M rows
* `people_companies(p_id*, c_id*)`: 2M rows, joining `people` and
  `companies`
* `people_companies(id*, p_id, c_id)`: 2M rows, identical data to
  `people_companies`, but with a synthetic ID added

`people_companies` has a compound primary key and a secondary index on `c_id`
to support reverse lookups.
`people_companies_id` has a single, synthetic primary key. There is a unique
secondary index on `p_id` + `c_id` and a secondary index on `c_id` to support
reverse lookups.

## Source data
In [src_lists](src_lists) there are first and last names. Those are combined to
create 1M distinct `people` records. There are also adjectives, nouns, and
suffixes. Those will be combined to create 1M `company` records. Since those IDs
are sequential, we can choose random int pairs between zero and 1M to make the
associative rows.

All of the above is done in [make_lists.py](make_lists.py), which will generate
data in trg_lists.

## Test

* Against MySQL and Postgres
  * Using the composite keyed associative table and then the synthetic keyed
    * Query for `people.name` values given `company.name` values (SQL `IN`)
    * Query for `company.name` values given `people.name` values (SQL `IN`)

These are done 100 times, providing 1000 random names for each query. Since the
query parsing and transfer overhead is not free, it is important to have as many
lookups across the associative entities as possible.

# Hypothesis
Secondary (non-clustered) indices are a map (B+ tree) between the secondary
index key and the primary key of the table. Any column not found in the
secondary index key or primary key that is used in a predicate must be retrieved
from the primary (clustered) index, effectively a second lookup on each row in
the result set. This is why [covering indices](https://www.google.com/search?q=covering+index) are a well-known
technique for improving read performance.

The secondary index on the `c_id` in the synthetic key table does not include
`p_id`, nor is `p_id` in the primary key. It must be converted to a covering
index (more space, page faults, etc.) to avoid that second lookup. Meanwhile,
the secondary `c_id` index on the compound key table includes `p_id` as part of
the primary key, so you don't need to cover over it.

# Results
## Size
This is kind of a slam-dunk for the compound-key case:

| engine   | synthetic | compound | overhead  |
| -------- | --------- | -------- | --------- |
| MySQL    |  139.73MB |  97.17MB |    +43.8% |
| Postgres |  368.26MB | 267.20MB |    +37.8% |

## Performance
### Company to Person (secs/query, 1000 items)

| Engine   | synthetic | compound | synth cost |
| -------- | --------- | -------- | ---------- |
| MySQL    |  0.073992 | 0.062318 |     18.73% |
| Postgres |  0.091934 | 0.090599 |      1.47% |

In MySQL the difference between synthetic and compound is obvious and large.
Postgres is small but present. See _problems_ below.

### Person to Company
| Engine   | synthetic | compound | synth cost |
| -------- | --------- | -------- | ---------- |
| MySQL    |  0.054877 | 0.055011 |     -0.24% |
| Postgres |  0.085135 | 0.085470 |     -0.39% |

The difference in performance here is near the margin of error. This is to be
expected as it is hitting the primary key in the compound case and a unique,
non-clustred index containing both columns in the synthetic case.

# Problems
* Even with 1M rows in the two data tables and 2M in the associative entities,
  the entirety of the tables fit into memory, so that makes it harder to see
  what is going on with respect to timing.
* While SQL Server is
 [very explicit](https://technet.microsoft.com/en-us/library/bb326635.aspx)
  about needing to go back to the clustered index, MySQL's `EXPLAIN` is not.
  Postgres will tell you in a sneaky fashion, with [`index only scan`](https://www.postgresql.org/docs/10/static/indexes-index-only-scans.html).
* Assumptions in the hypothesis about the structure of secondary indices in
  Postgres are incorrect
    * Postgres stores a map of secondary-index key to TID, not the primary key
      ([docs](https://www.postgresql.org/docs/current/static/indexam.html))
    * Better performance may be attained in this test by covering over the PK in
      the `c_id` key. This is easy to test and I will later.
    * MySQL's InnoDB works as described ([docs](https://dev.mysql.com/doc/refman/5.7/en/innodb-index-types.html))
