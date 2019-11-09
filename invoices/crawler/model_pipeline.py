from . import context


class SavePrizePipeline:

    def process_item(self, item, spider):
        prize_model = context.prize_model
        prize_model.add_prize(*self._to_prize_args(item))

    def _to_prize_args(self, item):
        return (
            item['type'],
            item['year'],
            item['month'],
            item['number'],
            self._to_prize(item['type'])
        )

    def _to_prize(self, prize_item_type):
        # TODO
        return 200